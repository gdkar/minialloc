#include <stdatomic.h>
int main(void) {
    atomic_int test = ATOMIC_VAR_INIT(123);
    return atomic_load(&test)==123;
}
