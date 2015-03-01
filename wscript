# vi: ft=python

import sys, os, re
sys.path.insert(0, os.path.join(os.getcwd(), 'waftools'))
sys.path.insert(0, os.getcwd())
from waflib.Configure import conf
from waflib import Utils
from waftools.checks.generic import *
from waftools.checks.custom import *

build_options = [
        {
        'name': '--libminialloc-shared',
        'desc': 'minialloc shared library',
        'default': 'enable',
        'func': check_true
    },   {
        'name': '--libminialloc-static',
        'desc': 'minialloc static library',
        'default': 'enable',
        'func': check_true
        },{ 'name':'libminialloc',
            'desc':'libminialloc. uh...',
            'req' :True, 
            'func':check_true,
            'deps_any':['libminialloc-shared','libminialloc-static']
    },{
        'name': '--build-date',
        'desc': 'whether to include binary compile time',
        'default': 'enable',
        'func': check_true
    }, {
        'name': '--optimize',
        'desc': 'whether to optimize',
        'default': 'enable',
        'func': check_true
    }, {
        'name': '--debug-build',
        'desc': 'whether to compile-in debugging information',
        'default': 'enable',
        'func': check_true
    },{
        'name': 'libdl',
        'desc': 'dynamic loader',
        'func': check_libs(['dl'], check_statement('dlfcn.h', 'dlopen("", 0)'))
    }, {
        'name': '--clang-database',
        'desc': 'generate a clang compilation database',
        'func': check_true,
        'default': 'enable',
    }
]
main_dependencies = [
    {
        'name': 'libm',
        'desc': '-lm',
        'func': check_cc(lib='m')
    }, {
        'name': 'posix',
        'desc': 'POSIX environment',
        # This should be good enough.
        'req' : 'true',
        'func': check_statement(['poll.h', 'unistd.h', 'sys/mman.h'],
            'struct pollfd pfd; poll(&pfd, 1, 0); fork(); int f[2]; pipe(f); munmap(f,0)'),
    }, {
        'name': 'pthreads',
        'desc': 'POSIX threads',
        'func': check_pthreads,
        'req': True,
        'fmsg': 'Unable to find pthreads support.'
    }, {
        'name': 'stdatomic',
        'desc': 'stdatomic.h',
        'func': check_stdatomic
    }, {
        'name': 'atomic-builtins',
        'desc': 'compiler support for __atomic built-ins',
        'func': check_libs(['atomic'],
            check_statement('stdint.h',
                'int64_t test = 0;'
                'test = __atomic_fetch_add(&test, 1, __ATOMIC_SEQ_CST)')),
        'deps_neg': [ 'stdatomic' ],
    }, {
        'name': 'sync-builtins',
        'desc': 'compiler support for __sync built-ins',
        'func': check_statement('stdint.h',
                    'int64_t test = 0;'
                    '__typeof__(test) x = ({int a = 1; a;});'
                    'test = __sync_fetch_and_add(&test, 1)'),
        'deps_neg': [ 'stdatomic', 'atomic-builtins' ],
    }, {
        'name': 'atomics',
        'desc': 'compiler support for usable thread synchronization built-ins',
        'func': check_true,
        'req' : True,
        'deps_any': ['stdatomic', 'atomic-builtins', 'sync-builtins'],
    }, {
        'name': 'librt',
        'desc': 'linking with -lrt',
        'deps': [ 'pthreads' ],
        'func': check_cc(lib='rt')
    }, {
        'name': '--shm',
        'desc': 'shm',
        'func': check_statement(['sys/types.h', 'sys/ipc.h', 'sys/shm.h'],
            'shmget(0, 0, 0); shmat(0, 0, 0); shmctl(0, 0, 0)')
    }, {
        'name': 'nanosleep',
        'desc': 'nanosleep',
        'func': check_statement('time.h', 'nanosleep(0,0)')
    }
        
]


_INSTALL_DIRS_LIST = [
    ('bindir',  '${PREFIX}/bin',      'binary files'),
    ('libdir',  '${PREFIX}/lib',      'library files'),
    ('confdir', '${PREFIX}/etc/mpv',  'configuration files'),

    ('incdir',  '${PREFIX}/include',  'include files'),

    ('datadir', '${PREFIX}/share',    'data files'),
    ('mandir',  '${DATADIR}/man',     'man pages '),
    ('docdir',  '${DATADIR}/doc/minialloc', 'documentation files'),
    ('zshdir',  '${DATADIR}/zsh/site-functions', 'zsh completion functions'),
]

def options(opt):
    opt.load('compiler_c')
    opt.load('waf_customizations')
    opt.load('features')

    group = opt.get_option_group("build and install options")
    for ident, default, desc in _INSTALL_DIRS_LIST:
        group.add_option('--{0}'.format(ident),
            type    = 'string',
            dest    = ident,
            default = default,
            help    = 'directory for installing {0} [{1}]' \
                      .format(desc, default))

    group.add_option('--variant',
        default = '',
        help    = 'variant name for saving configuration and build results')

    opt.parse_features('build and install options', build_options)
    optional_features = main_dependencies 
    opt.parse_features('optional features', optional_features)
    group = opt.get_option_group("optional features")

@conf
def is_optimization(ctx):
    return getattr(ctx.options, 'enable_optimize')

@conf
def is_debug_build(ctx):
    return getattr(ctx.options, 'enable_debug-build')

def configure(ctx):
    ctx.resetenv(ctx.options.variant)
    ctx.check_waf_version(mini='1.8.6')
    target = os.environ.get('TARGET')
    (cc, pkg_config, ar, windres) = ('cc', 'pkg-config', 'ar', 'windres')

    if target:
        cc         = '-'.join([target, 'gcc'])
        pkg_config = '-'.join([target, pkg_config])
        ar         = '-'.join([target, ar])
        windres    = '-'.join([target, windres])

    ctx.find_program(cc,          var='CC')
    ctx.find_program(pkg_config,  var='PKG_CONFIG')
    ctx.find_program(ar,          var='AR')
    for ident, _, _ in _INSTALL_DIRS_LIST:
        varname = ident.upper()
        ctx.env[varname] = getattr(ctx.options, ident)
        # keep substituting vars, until the paths are fully expanded
        while re.match('\$\{([^}]+)\}', ctx.env[varname]):
            ctx.env[varname] = Utils.subst_vars(ctx.env[varname], ctx.env)
    ctx.load('compiler_c')
    ctx.load('waf_customizations')
    ctx.load('dependencies')
    ctx.load('detections.compiler')
    ctx.load('detections.devices')
    ctx.parse_dependencies(build_options)
    ctx.parse_dependencies(main_dependencies)
    
    if not ctx.dependency_satisfied('build-date'):
        ctx.env.CFLAGS += ['-DNO_BUILD_TIMESTAMPS']

    if ctx.dependency_satisfied('clang-database'):
        ctx.load('clang_compilation_database')
    ctx.store_dependencies_lists()

def build(ctx):
    if ctx.options.variant not in ctx.all_envs:
        from waflib import Errors
        raise Errors.WafError(
            'The project was not configured: run "waf --variant={0} configure" first!'
                .format(ctx.options.variant))
    ctx.unpack_dependencies_lists()
    ctx.load('wscript_build')

def init(ctx):
    from waflib.Build import BuildContext, CleanContext, InstallContext, UninstallContext
    for y in (BuildContext, CleanContext, InstallContext, UninstallContext):
        class tmp(y):
            variant = ctx.options.variant

    # This is needed because waf initializes the ConfigurationContext with
    # an arbitrary setenv('') which would rewrite the previous configuration
    # cache for the default variant if the configure step finishes.
    # Ideally ConfigurationContext should just let us override this at class
    # level like the other Context subclasses do with variant
    from waflib.Configure import ConfigurationContext
    class cctx(ConfigurationContext):
        def resetenv(self, name):
            self.all_envs = {}
            self.setenv(name)
