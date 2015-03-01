import re
import os


def _build_man(ctx):
    ctx(
        name         = 'rst2man',
        target       = 'DOCS/man/mpv-redux.1',
        source       = 'DOCS/man/mpv.rst',
        rule         = '${RST2MAN} ${SRC} ${TGT}',
        install_path = ctx.env.MANDIR + '/man1')

    _add_rst_manual_dependencies(ctx)

def _all_includes(ctx):
    return [ctx.bldnode.abspath(), ctx.srcnode.abspath()] + \
            ctx.dependencies_includes()

def build(ctx):
    ctx.load('waf_customizations')
    ctx.load('generators.sources')


    sources = [
#        ( "osdep/win32/pthread.c",               "win32-internal-pthreads"),

    ]


    syms = False
    if ctx.dependency_satisfied('libminialloc'):
        ctx.load("syms")
        ctx(
            target       = "objects",
            source       = ctx.filtered_sources(sources),
            use          = ctx.dependencies_use(),
            includes     = _all_includes(ctx),
            features     = "c",
        )

    build_static = ctx.dependency_satisfied('libminialloc-static')
    build_shared = ctx.dependency_satisfied('libminialloc-shared')
    if build_shared or build_static:
        if build_shared:
            waftoolsdir = os.path.join(os.path.dirname(__file__), "waftools")
            ctx.load("syms", tooldir=waftoolsdir)
        vre = '^#define MINIALLOC_VERSION MA_MAKE_VERSION\((.*), (.*)\)$'
        libminialloc_header = ctx.path.find_node("include/minialloc.h").read()
        major, minor = re.search(vre, libminialloc_header, re.M).groups()
        libversion = major + '.' + minor + '.0'

        def _build_libminialloc(shared):
            features = "c "
            if shared:
                features += "cshlib syms"
            else:
                features += "cstlib"
            ctx(
                target       = "minialloc",
                source       = ctx.filtered_sources(sources),
                use          = ctx.dependencies_use(),
                includes     = [ctx.bldnode.abspath(), ctx.srcnode.abspath()] + \
                                ctx.dependencies_includes(),
                features     = features,
                export_symbols_def = "src/minialloc.def",
                install_path = ctx.env.LIBDIR,
                vnum         = libversion,
            )
        if build_shared:
            _build_libminialloc(True)
        if build_static:
            _build_libminialloc(False)
        def get_deps():
            res = ""
            for k in ctx.env.keys():
                if k.startswith("LIB_") and k != "LIB_ST":
                    res += " ".join(["-l" + x for x in ctx.env[k]]) + " "
            return res
        ctx(
            target       = 'src/minialloc.pc',
            source       = 'src/minialloc.pc.in',
            features     = 'subst',
            PREFIX       = ctx.env.PREFIX,
            LIBDIR       = ctx.env.LIBDIR,
            INCDIR       = ctx.env.INCDIR,
            VERSION      = libversion,
            PRIV_LIBS    = get_deps(),
        )
        headers = ["minialloc.h"]
        for f in headers:
            ctx.install_as(ctx.env.INCDIR + '/' + f, 'include/' + f)
        ctx.install_as(ctx.env.LIBDIR + '/pkgconfig/minialloc.pc', 'src/minialloc.pc')

