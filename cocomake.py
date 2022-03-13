import os
import argparse
import subprocess
import shutil

from time import time 
from datetime import datetime, timedelta
from timeit import default_timer as timer

paths = {}
tools = {}
toolchains = {}
timestamps = {}
banks = {}

outfile = ''
image = ''

temp_files = []

compile = False

def stage(tool, name, ext):

    if tool not in tools:
        print('Unknown tool', tool)

    toolpath = tools[tool].split('->')[0]
    outext = tools[tool].split('->')[1]

    cmd = toolpath + ' ' + paths['src'] + '\\' + name + '.' + ext

    if compile:
        print('\tExecuting ' + tool + ' with ' + name + '.' + ext)
        subprocess.run(cmd)

    return (name, outext)

def link(cfg):
    f = open(cfg)

    ps = f.readlines()

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

            print(str(nameext) + '>')

            lastmod = os.path.getmtime(paths['src'] + '\\' + nameext)

            if nameext in timestamps:

                global compile

                if str(lastmod) == timestamps[nameext]:
                    print('\t' + nameext + ' is up to date, skip')
                    compile = False
                else:
                    timestamps[nameext] = lastmod
                    compile = True
            else:
                compile = True
                timestamps[nameext] = lastmod

            if compile:
                print('\tMaking ' + nameext)

            if ext not in toolchains:
                print('Unknown extension', ext)
                exit()

            toolchain = toolchains[ext].split('->')

            for tool in toolchain:
                if tool != '':
                    (name, ext) = stage(tool, name, ext)
                    if compile:
                        temp_files.append(name + '.' + ext)
                else:
                    # for zero toolchain (.img)
                    if compile:
                        shutil.copyfile(paths['src'] + '\\' + name + '.' + ext, paths['temp'] + '\\' + name + '.' + ext)
                
            path = ''

            if compile:
                path = paths['src'] + '\\' + name + '.' + ext
            else:
                path = paths['temp'] + '\\' + name + '.' + ext

            f = open(path)

            bytes = f.read()[9:]

            image += bytes

            f.close()

            print()
            
        else:
            image += "00\n" * 256

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

def move_temp_files():
    for p in temp_files:
        os.replace(paths['src'] + '\\' + p, paths['temp'] + '\\' + p)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Cocomake')
    parser.add_argument('config_file',type=str, help='[config_file].cocomake')

    parser.add_argument('-r',dest='recomp',action='store_const',const=True,default=False, help="force recompile")
    parser.add_argument('-c',dest='cleanup',action='store_const',const=True,default=False, help="cleanup temp files")
    parser.add_argument('-i',dest='init',action='store_const',const=True,default=False, help="init project")
    args = parser.parse_args()

    paths['root'] = os.getcwd()
    read_paths()

    if args.recomp:
        timestamp_cleanup()

    if args.cleanup:
        temp_cleanup()

    read_tools()
    read_toolchains()
    read_timestamps()

    link(args.config_file)

    write_image()
    write_timestamps()

    move_temp_files()

    # -i -c w/o compile
    # pretty output color = 0000-00FF: all_ff.img ...
    