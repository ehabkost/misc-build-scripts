#include <stdio.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <unistd.h>

#define BELOW_47BIT 0x7ffff8000000ull
#define ABOVE_47BIT 0x800008000000ull

int main(int argc, char *argv[])
{
    void *p1 = mmap((void*)BELOW_47BIT, 0x4000000, PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
    if (p1 != MAP_FAILED) {
        printf("allocated p1 at %p\n", p1);
    } else {
        perror("allocating below 47-bit boundary");
    }
    void *p2 = mmap((void*)ABOVE_47BIT, 0x4000000, PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
    if (p2 != MAP_FAILED) {
        printf("allocated p2 at %p\n", p2);
    } else {
        perror("allocating above 47-bit boundary");
    }
    printf("Check /proc/%ld/maps\n", (long)getpid());
    sleep(300);
    return 0;
}