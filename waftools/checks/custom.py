from waftools.inflectors import DependencyInflector
from waftools.checks.generic import *
from waflib import Utils
import os

__all__ = ['check_pthreads', 'check_stdatomic']

pthreads_program  = load_fragment('pthreads.c')
stdatomic_program = load_fragment('stdatomic.c')
def check_pthread_flag(ctx, dependency_identifier):
    checks = [
        check_cc(fragment = pthreads_program, cflags = '-pthread'),
        check_cc(fragment = pthreads_program, cflags = '-pthread',
                                            linkflags = '-pthread') ]

    for fn in checks:
        if fn(ctx, dependency_identifier):
            return True
    return False
def check_stdatomic(ctx,dependency_identifier):
    ctx.env.CFLAGS += ['-std=gnu11']
    if check_cc(fragment=stdatomic_program,cflags='-std=gnu11'):
        return True
    return False
def check_pthreads(ctx, dependency_identifier):
    if check_pthread_flag(ctx, dependency_identifier):
        return True
    platform_cflags = {
        'linux':   '-D_REENTRANT',
        'freebsd': '-D_THREAD_SAFE',
        'netbsd':  '-D_THREAD_SAFE',
        'openbsd': '-D_THREAD_SAFE',
    }.get(ctx.env.DEST_OS, '')
    libs    = ['pthreadGC2', 'pthread']
    checkfn = check_cc(fragment=pthreads_program, cflags=platform_cflags)
    checkfn_nocflags = check_cc(fragment=pthreads_program)
    for fn in [checkfn, checkfn_nocflags]:
        if check_libs(libs, fn)(ctx, dependency_identifier):
            return True
    return False

