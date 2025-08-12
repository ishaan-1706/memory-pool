#include "pool.h"
#include <stdio.h>

int main() {
    // Initialize a pool of 1 MiB
    size_t pool_size = 1024 * 1024;
    MemoryPool* pool = pool_init(pool_size);
    if (!pool) {
        fprintf(stderr, "Failed to initialize memory pool\n");
        return 1;
    }

    // Simple alloc/free cycle
    void* a = pool_alloc(pool, 64);
    void* b = pool_alloc(pool, 128);
    void* c = pool_alloc(pool, 256);

    pool_free(pool, b);
    pool_free(pool, a);

    // Gather fragmentation stats
    FragmentStats fs;
    pool_get_fragmentation(pool, &fs);

    // Print fragmentation report
    printf("After simple smoke test:\n");
    printf("  total pool size      = %zu bytes\n", pool_size);
    printf("  number of free blocks = %zu\n", fs.num_fragments);
    printf("  total free memory     = %zu bytes\n", fs.total_free_bytes);
    printf("  largest free block    = %zu bytes\n", fs.largest_fragment);
    printf("  smallest free block   = %zu bytes\n", fs.smallest_fragment);

    // Clean up
    pool_destroy(pool);
    return 0;
}
