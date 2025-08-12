#ifndef MEMORY_POOL_H
#define MEMORY_POOL_H

#include <stddef.h>

// Opaque pool type
typedef struct MemoryPool MemoryPool;

// Fragmentation statistics
typedef struct {
    size_t num_fragments;       // count of free blocks
    size_t total_free_bytes;    // sum of all free‐block sizes
    size_t largest_fragment;    // max free‐block size
    size_t smallest_fragment;   // min free‐block size
} FragmentStats;

// Pool API
MemoryPool* pool_init(size_t total_bytes);
void*       pool_alloc(MemoryPool* pool, size_t size);
void        pool_free(MemoryPool* pool, void* ptr);
void        pool_destroy(MemoryPool* pool);

// Gather fragmentation stats (populate stats struct)
void        pool_get_fragmentation(MemoryPool* pool, FragmentStats* stats);

#endif // MEMORY_POOL_H
