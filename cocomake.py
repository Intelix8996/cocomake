#
#   Cocomake - versatile incremental build system
#   Written by Nikolay Repin
#   2022
#

import os
import argparse
import subprocess
import shutil
import sys

from datetime import timedelta
from timeit import default_timer as timer

from termcolor import colored

COLORED_OUTPUT = True
VERBOSE = False
RECOMPILE = False

paths = {}
tools = {}
toolchains = {}
timestamps = {}
banks = {}

outfile = ''
image = ''

temp_files = []

compile_ = False


def stage(tool, name, ext):
    if tool not in tools:
        error('Unknown tool ' + tool)
        sys.exit()

    tokens = tools[tool].split('->')

    if len(tokens) == 2:
        tokens.append('')

    tool_path, out_ext, postfix = tokens

    cmd = tool_path + ' ' + paths['src'] + '\\' + name + '.' + ext

    if compile_:
        if VERBOSE:
            message('\tExecuting ' + tool + ' with ' + name + '.' + ext)
        subprocess.run(cmd)

    return name + postfix, out_ext


def link(cfg):
    if RECOMPILE:
        message('Force recompile all files...')
        print()

    start = timer()

    f = open(cfg)

    ps = f.readlines()

    if len(ps) == 0:
        error('Empty config file')
        sys.exit()

    global outfile
    outfile = ps[0].replace('\n', '')

    ps = ps[1:]

    for l in ps:
        l = l.replace('\n', '').split(':')
        banks[int(l[0])] = l[1]

    mx = max(banks.keys())

    global image
    image = "v2.0 raw\n"

    for i in range(mx + 1):

        if i in banks.keys():

            nameext = banks[i]
            name = nameext.split('.')[0]
            ext = nameext.split('.')[1]

            lastmod = os.path.getmtime(paths['src'] + '\\' + nameext)

            if nameext in timestamps:

                global compile_

                if str(lastmod) == timestamps[nameext]:
                    compile_ = False
                else:
                    timestamps[nameext] = lastmod
                    compile_ = True
            else:
                compile_ = True
                timestamps[nameext] = lastmod

            if compile_:
                message(str(i) + '>' + nameext)
            else:
                if COLORED_OUTPUT or VERBOSE:
                    info(str(i) + '>' + nameext)

            if VERBOSE:
                if compile_:
                    message('\tMaking ' + nameext)
                else:
                    info('\t' + nameext + ' is up to date, skip')

            if ext not in toolchains:
                error(f'Unknown extension: {ext}')
                sys.exit()

            toolchain = toolchains[ext].split('->')

            for tool in toolchain:
                if tool != '':
                    (name, ext) = stage(tool, name, ext)
                    if compile_ and not os.path.isfile(paths['src'] + '\\' + name + '.' + ext):
                        error('Something went wrong with ' + tool + ' and ' + name)
                        sys.exit()
                    if compile_:
                        temp_files.append(name + '.' + ext)
                else:
                    # for zero toolchain (.img)
                    if compile_:
                        shutil.copyfile(paths['src'] + '\\' + name + '.' + ext, paths['temp'] + '\\' + name + '.' + ext)

            path = ''

            if compile_:
                path = paths['src'] + '\\' + name + '.' + ext
            else:
                path = paths['temp'] + '\\' + name + '.' + ext

            f = open(path)

            _bytes = f.read()[9:]

            image += _bytes

            f.close()

        else:
            image += "00\n" * 256

    end = timer()

    message('\nGenerated ' + outfile + ' in ' + str(timedelta(seconds=end - start)))


def read_timestamps():
    f = open('timestamps')

    ps = f.readlines()

    for l in ps:
        l = l.replace('\n', '').split('=')
        timestamps[l[0]] = l[1]

    f.close()


def read_tools():
    f = open('tools')

    ps = f.readlines()

    for l in ps:
        l = l.replace('\n', '').split('=')
        tools[l[0]] = l[1]

    f.close()


def read_toolchains():
    f = open('toolchains')

    ps = f.readlines()

    for l in ps:
        l = l.replace('\n', '').split('=')
        toolchains[l[0]] = l[1]

    f.close()


def read_paths():
    f = open('paths')

    ps = f.readlines()

    for l in ps:
        l = l.replace('\n', '').split('=')
        paths[l[0]] = l[1]

    f.close()


def write_image():
    wfile = open(paths['output'] + '\\' + outfile, 'w')

    wfile.write(image)

    wfile.close()


def write_timestamps():
    wfile = open('timestamps', 'w')

    for key in timestamps.keys():
        wfile.write(str(key) + '=' + str(timestamps[key]) + '\n')

    wfile.close()


def temp_cleanup():
    for f in os.listdir(paths['temp']):
        os.remove(os.path.join(paths['temp'], f))
    timestamp_cleanup()


def timestamp_cleanup():
    wfile = open('timestamps', 'w')

    wfile.write('')

    wfile.close()


def init_project():
    path = paths['root']

    if os.path.isfile(path + '\\' + 'paths'):
        warning('This action will override current configuration')
        if COLORED_OUTPUT:
            print(colored('Continue? (y/n) ', 'yellow'), end='')
        else:
            print('Continue? (y/n) ', end='')

        answer = input()

        if answer == 'y':
            pass
        elif answer == 'n':
            sys.exit()
        else:
            error('Invalid answer ' + answer)
            sys.exit()

    info('Initialising project at ' + path + '...')

    f = open(path + '\\' + 'paths', 'w')

    f.write('src=\n')
    f.write('temp=\n')
    f.write('output=')

    f.close()

    f = open(path + '\\' + 'timestamps', 'w')
    f.close()

    f = open(path + '\\' + 'toolchains', 'w')
    f.close()

    f = open(path + '\\' + 'tools', 'w')
    f.close()

    f = open(path + '\\' + 'default.cocomake', 'w')
    f.close()

    message('Success!')


def move_temp_files():
    for p in temp_files:
        os.replace(paths['src'] + '\\' + p, paths['temp'] + '\\' + p)


def to_hex_string(n1, n2):
    return '{0:0{1}X}'.format(n1, 4) + '-{0:0{1}X}:'.format(n2, 4)


def print_map():
    mx = max(banks.keys())
    message('\n' + outfile + ':')

    for i in range(mx + 1):

        s = to_hex_string(i * 256, ((i + 1) * 256) - 1)

        if i in banks.keys():
            message(s + ' ' + banks[i])
        else:
            message(s + ' -')


def add_to_makefile(cfg, add):
    empty = False
    num = int(add[0])
    add = add[1:]

    f = open(cfg)

    readtext = f.read()

    lastchar = '0'

    if len(readtext) != 0:
        lastchar = readtext[len(readtext) - 1]
    else:
        empty = True

    f.close()

    f = open(cfg, 'a')

    if lastchar != '\n' and not empty:
        f.write('\n')

    for s in add:
        f.write(str(num) + ':' + s + '\n')
        num += 1

    f.close()


def start_debug(file):
    info('Debugging ' + file)

    if 'debug' not in tools.keys():
        error('No debug configuration')
        sys.exit()

    path = tools['debug'] + ' ' + paths['src'] + '\\' + file

    subprocess.run(path)


def print_info():
    info('|' + '-' * 55 + '|')
    info('|' + ' ' * 55 + '|')
    info('|' + ' ' * 5 + 'Cocomake - versatile incremental build system' + ' ' * 5 + '|')
    info('|' + ' ' * 15 + 'Written by Nikolay Repin' + ' ' * 16 + '|')
    info('|' + ' ' * 55 + '|')
    info('|' + '-' * 55 + '|')


def info(text):
    if COLORED_OUTPUT:
        print(colored(text, 'blue'))  # mb cyan
    else:
        print(text)


def message(text):
    if COLORED_OUTPUT:
        print(colored(text, 'green'))
    else:
        print(text)


def error(text):
    if COLORED_OUTPUT:
        print(colored('Error: ' + text, 'red'))
    else:
        print('Error: ' + text)


def warning(text):
    if COLORED_OUTPUT:
        print(colored("Warning: " + text, 'yellow'))
    else:
        print("Warning: " + text)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Cocomake - versatile incremental build system')
    parser.add_argument('config_file', type=str, nargs='?', default='', help='[config_file].cocomake')

    parser.add_argument('-r', dest='recomp', action='store_const', const=True, default=False, help="force recompile")
    parser.add_argument('-c', dest='cleanup', action='store_const', const=True, default=False,
                        help="cleanup temp files")
    parser.add_argument('-init', dest='init', action='store_const', const=True, default=False, help="init project")
    parser.add_argument('-a', dest='add', type=str, action='store', nargs='+', help="add files to config file")
    parser.add_argument('-d', dest='debug', type=str, action='store', nargs='?', help="debug a file")
    parser.add_argument('-v', dest='verbose', action='store_const', const=True, default=False, help="verbose output")
    parser.add_argument('-m', dest='map', action='store_const', const=True, default=False, help="print memory map")
    parser.add_argument('-bw', dest='bw', action='store_const', const=True, default=False, help="monocrome output")
    parser.add_argument('-i', '-info', dest='info', action='store_const', const=True, default=False, help="show info")
    args = parser.parse_args()

    COLORED_OUTPUT = not args.bw
    VERBOSE = args.verbose

    paths['root'] = os.getcwd()

    if args.info:
        print_info()
        sys.exit()

    if args.init:
        init_project()
        sys.exit()

    read_paths()
    read_tools()
    read_toolchains()

    if args.debug:
        start_debug(args.debug)
        sys.exit()

    if args.cleanup:
        info('Removing temporary files...')
        temp_cleanup()
        message('Success!')
        sys.exit()

    if args.recomp:
        RECOMPILE = True
        timestamp_cleanup()

    read_timestamps()

    if args.config_file != '':
        if args.add is not None:
            add_to_makefile(args.config_file, args.add)
            sys.exit()
        else:
            link(args.config_file)
    else:
        error('No config file!')
        info('You should specify .cocomake file when calling cocomake')
        sys.exit()

    write_image()
    write_timestamps()

    move_temp_files()

    if args.map:
        print_map()

    # compile to exe
    # path.join
