# Cocomake
#### Versatile incremental build system


---


# Overview
**Cocomake** is a build system that allow you to compile big projects into Logisim .img files. It is mainly created to work with Coco-de-Mer infrastructure, but can be easily retargeted.

# Getting Started
### Installing 
+ Clone repo
+ Download binary (avaliable only for win64)

Additionally you can add cocomake to `PATH`

### Setting up a project

1. Get cocomake.
2. Create a folder for your project.
3. From this folder call `cocomake -init` to initialize your project.

> If your terminal can't display color you will get garbage in the output. To prevent this use `-bw` flag, it will switch output to black&white mode.

Then `paths`, `toolchains`, `tools` and `timestamps` files will be created.

4. Now create folders for source files, temporary files and output files. Then define `src`, `temp`, `output` paths in `paths` file in format `[var]=[path]`. 

Your `paths` file should look like this:
```
src=C:\path\to\source\files
temp=C:\path\to\temp\files
output=C:\path\to\output\files
```

5. Define tools in `tools` file in format `[name]=[cmd]->[output extension]` or `[name]=[cmd]->[output extension]->[output postfix]`. Additionaly you can define debug configuration there `debug=[cmd]` *(without ->)*.

Your `paths` file should look like this:
```
linker=C:\path\to\linker\linker.exe->img
assembler=C:\path\to\assembler\assembler.exe->obj
debug=C:\path\to\debugger\debugger.exe
```

So, there we adder a linker that produces files with .img extension and assembler that produces files with .obj extension.

6. Define toolchains in `toolchains` file in format `[ext]=[tool1]->[tool2]->...->[tool]`.

Your `toolchains` file should look like this:

>Note: [tool]s are names of tools you defined in `tools` file 

```
asm=prerocessor->assembler->linker
img=
```

In this example, we define that files with .asm extension will go through prerocessor, assembler and linker and then they will be linked to final image. Also .img files will be directly linked to final image.

7. Create config file *(theese are ones with .cocomake extension)*. Cocomake will create one called default.cocomake when initializing the project.

Config file looks like this:

```
[output file]
[n]:[file]
...
[n]:[file]
```

First line defines the name of output file.
Next lines define which file from `src` directoty will be linked to which bank

For example:
```
firmware.img
0:first_file.asm
1:second_file.asm
3:third_file.asm
4:some_image.img
```

Then you project is set up.
You can create make it with `cocomake [config]` command.
For example, `cocomake default.cocomake`.

# Command Line Arguments

#### You can get full list of arguments with `cocomake -h`

+ `-r` - force recompile all files. *Usage:* `cocomake -r [config]`
+ `-c` - cleanup temporary files. *Usage:* `cocomake -c`
+ `-a` - add files to specified config file. *Usage:* `cocomake -a [config] [file1] [file2] ... [file]`. *Note: [file] - just names of files in `src` folder*
+ `-d` - debug a file (open a debugger with specified file). *Usage:* `cocomake -d [file]`. *Note: [file] - path to file relative to `src` folder*
+ `-v` - verbose output. *Usage:* `cocomake -v [config]`
+ `-m` - print memory map afer making image.  *Usage:* `cocomake -m [config]`
+ `-bw` - switch output to black and white mode.  *Usage:* `cocomake -bw ...`
+ `-init` - initialize project.  *Usage:* `cocomake -init`
+ `-i`, `-info` - print about window.  *Usage:* `cocomake -i`, `cocomake -info`

You can also combine some arguments. Example: `cocomake -m -bw -v default.cocomake`

# Credits
Written by Nikolay Repin in 2022.
