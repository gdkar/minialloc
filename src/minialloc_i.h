#ifndef _MINIALLOC_I_H_
#define _MINIALLOC_I_H_
#include "minialloc.h"

#define MA_PRINTF_ATTRIBUTE(a1,a2) __attribute__((format(printf,a1,a2)))
#define MA_INLINE                  static inline
#define MA_NO_INLINE               __attribute__((noinline))
#define MA_NORETURN                __attribute__((noreturn))
#define MA_THREAD_LOCAL            __thread
#define ma_likely(x)               __builtin_expect(!!(x),1)
#define ma_unlikely(x)             __builtin_expect(!!(x),0)

#define MA_ROUND_DOWN(x,align)     ((x)&~((align)-1)
#define MA_ROUND_UP(x,align)       MA_ROUND_DOWN((x)+((align)-1),(align))
#define MA_IS_POW_2(x)             ((x) && !((x) & ((x)-1)))

#define ma_memory_barrier()        __asm__ volatile ("sync" : : : "memory")
#define MA_LOCK_PREFIX             "lock ; "

#define MA_CACHELINE_BITS          (6)
#define MA_CACHELINE_SIZE          (1ULL<<MA_CACHELINE_BITS)
#define MA_CACHELINE_MASK          (MA_CACHELINE_SIZE-1)
#define MA_ALIGNED(x)              __attribute__((aligned(x)))
#define MA_CACHE_ALIGNED           MA_ALIGNED(MA_CACHELINE_SIZE)
#define MA_PAGE_BITS               (12)
#define MA_PAGE_SIZE               (1ULL<<MA_PAGE_SIZE)
#define MA_PAGE_MASK               (MA_PAGE_SIZE-1)
#define MA_HUGE_PAGE_BITS          (22)
#define MA_HUGE_PAGE_SIZE          (1ULL<<MA_HUGE_PAGE_SIZE)
#define MA_HUGE_PAGE_MASK          (MA_HUGE_PAGE_SIZE-1)
#define MA_VMA_BITS                (48)
#define MA_VMA_MASK                ((1ULL<<MA_VMA_BITS)-1)
#define MA_TAG_BITS                (16)
#define MA_TAG_MASK                (~MA_VMA_MASK)
#define MA_VMA_GET(x)              (((uint64_t)x)&MA_VMA_MASK)
#define MA_TAG_GET(x)              (((uint64_t)x)>>MA_VMA_BITS)
#define MA_TAG_VMA(x,tag)          ((((uint64_t)tag)<<MA_VMA_BITS)|MA_VMA_GET(x))

typedef struct atomic_int_fast128_t MA_ALIGNED(16) {
  atomic_int_fast64_t lo;
  atomic_int_fast64_t hi;
}atomic_int_fast128_t;


MA_INLINE int atomic_compare_exchange_8 (atomic_int_fast64_t *p, atomic_int_fast64_t *o, const atomic_int_fast64_t n){
  char r;
  __asm__ volatile ("cmpxchg8b %0;setz %2\n\t"
      : "=m"(*p), "=A", ( *o), "=r" ( r)
      :  "m"(*p),  "A", ( *o),  "b" ( n)
      :  "cc", "rbx", "rcx", "rdx", "memory");
  return r;
}
MA_INLINE int atomic_compare_exchange_16(atomic_int_fast128_t *p, atomic_int_fast128_t *o, const atomic_int_fast128_t n){
  char r;
  __asm__ volatile ("cmpxchg16b %0;setz %3\n\t",
      :"=m"(*p), "=d"(o->hi), "=a"(o->lo), "=r"(r)
      : "m"(*p),  "d"(o->hi),  "a"(o->lo),  "c" (n.hi), "b" (n.lo)
      : "cc", "rbx", "rcx", "rdx", "memory"
      );
  return r;
}
#endif
