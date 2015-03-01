#ifndef MINIALLOC_H
#define MINIALLOC_H

#ifndef _ISOC11_SOURCE
#define _ISOC11_SOURCE 1
#endif
#define MA_MAKE_VERSION(major,minor) (((major)<<16)|(minor)|(0UL))
#define MINIALLOC_VERSION MA_MAKE_VERSION(0, 0)
#include <stdatomic.h>
#include <stdint.h>
#include <stddef.h>
#include <sys/types.h>

void*        malloc(size_t size);
void*       realloc(void *ptr, size_t size);
void*        calloc(size_t nmemb, size_t size);
void*        valloc(size_t size);
void*       pvalloc(size_t size);
void* aligned_alloc(size_t align, size_t size);
void*      memalign(size_t align, size_t size);
int  posix_memalign(void **pptr, size_t align, size_t size);
void           free(void *ptr);
#endif
