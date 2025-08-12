#include "pool.h"
#include <windows.h>
#include <psapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define NUM_OPS 100000
#define MIN_SIZE 16
#define MAX_SIZE 256

// Timer utility
static double elapsed_ms(LARGE_INTEGER s, LARGE_INTEGER e, LARGE_INTEGER f) {
    return (double)(e.QuadPart - s.QuadPart) * 1000.0 / f.QuadPart;
}

// Get process RSS in KB
size_t get_rss_kb() {
    PROCESS_MEMORY_COUNTERS pmc;
    GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc));
    return pmc.WorkingSetSize / 1024;
}

void bench_malloc(void** ptrs) {
    for (int i = 0; i < NUM_OPS; ++i) {
        size_t sz = MIN_SIZE + rand() % (MAX_SIZE - MIN_SIZE + 1);
        ptrs[i] = malloc(sz);
    }
    for (int i = 0; i < NUM_OPS; ++i) free(ptrs[i]);
}

void bench_pool(MemoryPool* pool, void** ptrs) {
    for (int i = 0; i < NUM_OPS; ++i) {
        size_t sz = MIN_SIZE + rand() % (MAX_SIZE - MIN_SIZE + 1);
        ptrs[i] = pool_alloc(pool, sz);
    }
    for (int i = 0; i < NUM_OPS; ++i) pool_free(pool, ptrs[i]);
}

int main() {
    srand((unsigned)time(NULL));
    void* ptrs[NUM_OPS];
    LARGE_INTEGER freq, t0, t1;
    QueryPerformanceFrequency(&freq);

    // --- malloc/free benchmark ---
    QueryPerformanceCounter(&t0);
    bench_malloc(ptrs);
    QueryPerformanceCounter(&t1);
    double t_malloc = elapsed_ms(t0, t1, freq);
    size_t mem_malloc = get_rss_kb();

    // --- pool benchmark ---
    MemoryPool* pool = pool_init(NUM_OPS * MAX_SIZE);
    QueryPerformanceCounter(&t0);
    bench_pool(pool, ptrs);
    QueryPerformanceCounter(&t1);
    double t_pool = elapsed_ms(t0, t1, freq);
    size_t mem_pool = get_rss_kb();

    // --- fragmentation stats for pool ---
    FragmentStats fs;
    pool_get_fragmentation(pool, &fs);

    // --- report ---
    printf("malloc/free: time = %.2f ms, RSS = %zu KB, frag = N/A\n",
           t_malloc, mem_malloc);
    printf("pool alloc:  time = %.2f ms, RSS = %zu KB, "
           "fragments = %zu, total_free = %zu KB, largest = %zu B, smallest = %zu B\n",
           t_pool, mem_pool,
           fs.num_fragments,
           fs.total_free_bytes / 1024,
           fs.largest_fragment,
           fs.smallest_fragment);

    pool_destroy(pool);
    return 0;
}
