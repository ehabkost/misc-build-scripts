#include <stdio.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <unistd.h>

#define ABOVE_47BIT 0x800008000000ull

int main(int argc, char *argv[])
{   
    void *p = mmap((void*)ABOVE_47BIT, 0x4000000, PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED, -1, 0);
    if (p != MAP_FAILED) {
        printf("allocated p at %p\n", p);
	printf("5-level paging available!\n");
    } else {
        perror("allocating above 47-bit boundary");
	printf("5-level paging NOT available\n");
    }
    return 0;
}

