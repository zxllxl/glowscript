from __future__ import print_function, division

# This is the original Python 2.7 build file, used in building GlowScript
# according to the scheme described in docs/MakingNewVersion.txt.
# A more sophisticated build program is build_cli.py contributed by Iblis Lin.
"""This python program converts various parts of glowscript from the most
convenient format for modification into the most convenient format for
deployment.

* Take shaders from shaders/*.shader and combine them into lib/glow/shaders.gen.js

TODO

* Come up with a less painful model for development than running this after every change
* Combine and minify lib/*.js into ide.min.js, run.min.js, and embed.min.js
"""

from glob import glob
import re, os, subprocess

shader_file = ["Export({ shaders: {"]
for fn in sorted(glob("shaders/*.shader")):
    name = re.match(r"^shaders[/\\]([^.]+).shader$", fn).group(1)
    f = open(fn, "rt").read()
    shader_file.append( '"' + name + '":' + repr(f) + "," )
shader_file.append("}});")
shader_file = "\n".join(shader_file)
open("lib/glow/shaders.gen.js", "wb").write(shader_file)

version = "3.2"
# TODO: Extract this information from run.js

glowscript_libraries = {
    "run": [
        "../lib/jquery/"+"2.1"+"/jquery.mousewheel.js", # use 2.1 lib with later versions
        "../lib/flot/jquery.flot.js",
        "../lib/flot/jquery.flot.crosshair_GS.js",
        "../lib/plotly.js",
        "../lib/opentype/poly2tri.js",
        "../lib/opentype/opentype.js",
        "../lib/glMatrix.js",
        "../lib/webgl-utils.js",
        "../lib/glow/property.js",
        "../lib/glow/vectors.js",
        "../lib/glow/mesh.js",
        "../lib/glow/canvas.js",
        "../lib/glow/orbital_camera.js",
        "../lib/glow/autoscale.js",
        "../lib/glow/WebGLRenderer.js",
        "../lib/glow/graph.js",
        "../lib/glow/color.js",
        "../lib/glow/shapespaths.js",
        "../lib/glow/primitives.js",
        "../lib/glow/api_misc.js",
        "../lib/glow/extrude.js",
        "../lib/glow/shaders.gen.js"
        ],
    "compile": [
        "../lib/compiling/GScompiler.js",
        "../lib/compiling/acorn.js",
        "../lib/compiling/papercomp.js"
        ],
    "RScompile": [
        "../lib/rapydscript/compiler.js",
        "../lib/compiling/GScompiler.js",
        "../lib/compiling/acorn.js",
        "../lib/compiling/papercomp.js"
        ],
    "RSrun": [
        "../lib/rapydscript/runtime.js" # needed only for exporting a program
        ],
    "ide": []
    }

def combine(inlibs):
    # Apparently uglify moves the following string to the end of the package.
    # "(function(){x})();" appears at the both the start and the end of the package.
    all = [
        "/*This is a combined, compressed file.  Look at https://github.com/BruceSherwood/glowscript for source code and copyright information.*/",
        ";(function(){})();"
        ]
    for fn in inlibs:
        if fn.startswith("../"): fn = fn[3:]
        all.append( open(fn, "r").read() )
    return "\n".join(all)

env = os.environ.copy()
env["NODE_PATH"] = "build-tools/UglifyJS"

def minify(inlibs, inlibs_nomin, outlib):
    all = combine(inlibs)
    outf = open(outlib, "wb")

    if True: # minify if True
        uglify = subprocess.Popen( "build-tools/node.exe build-tools/Uglify-ES/uglify-es/bin/uglifyjs",
            stdin=subprocess.PIPE,
            stdout=outf,
            stderr=outf, # write uglify errors into output file
            env=env
            )
        uglify.communicate( all )
        rc = uglify.wait()
        if rc != 0:
            print("Something went wrong")
    else:
        outf.write(all)
    outf.write( combine(inlibs_nomin) )
    outf.close()

minify( glowscript_libraries["run"], [], "package/glow." + version + ".min.js" )
print('Finished glow run-time package\n')
minify( glowscript_libraries["compile"], [], "package/compiler." + version + ".min.js" )
print('Finished JavaScript compiler package\n')
minify( glowscript_libraries["RScompile"], [], "package/RScompiler." + version + ".min.js" )
print('Finished RapydScript compiler package\n')

# For GlowScript 3.1 runtime.js had the encoding "UCS-2 LE BOM" which the Uglify
# machinery could not handle. Using (on Windows) notepad++ the encoding was changed
# to "UTF-8" which solved the problem.
minify( glowscript_libraries["RSrun"], [], "package/RSrun." + version + ".min.js" )
print('Finished RapydScript run-time package')
