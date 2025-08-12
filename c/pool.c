#include "pool.h"
#include <stdlib.h>
#include <string.h>

// Free‐list node
typedef struct FreeBlock {
    size_t size;
    struct FreeBlock* next;
} FreeBlock;

struct MemoryPool {
    void*      buffer;
    size_t     total;
    FreeBlock* free_list;
};

MemoryPool* pool_init(size_t total_bytes) {
    MemoryPool* p = malloc(sizeof(*p));
    if (!p) return NULL;
    p->buffer = malloc(total_bytes);
    if (!p->buffer) { free(p); return NULL; }
    p->total = total_bytes;
    p->free_list = (FreeBlock*)p->buffer;
    p->free_list->size = total_bytes;
    p->free_list->next = NULL;
    return p;
}

void* pool_alloc(MemoryPool* p, size_t size) {
    FreeBlock **prev = &p->free_list, *curr = p->free_list;
    size = (size + sizeof(void*) - 1) & ~(sizeof(void*) - 1);
    while (curr) {
        if (curr->size >= size + sizeof(FreeBlock)) {
            void* user_ptr = (char*)curr + sizeof(FreeBlock);
            size_t rem = curr->size - size - sizeof(FreeBlock);
            if (rem > sizeof(FreeBlock)) {
                FreeBlock* nextb = (FreeBlock*)((char*)user_ptr + size);
                nextb->size = rem;
                nextb->next = curr->next;
                *prev = nextb;
            } else {
                *prev = curr->next;
            }
            return user_ptr;
        }
        prev = &curr->next;
        curr = curr->next;
    }
    return NULL;
}

void pool_free(MemoryPool* p, void* ptr) {
    if (!ptr) return;
    FreeBlock* blk = (FreeBlock*)((char*)ptr - sizeof(FreeBlock));
    blk->next = p->free_list;
    p->free_list = blk;
}

void pool_destroy(MemoryPool* p) {
    if (!p) return;
    free(p->buffer);
    free(p);
}

void pool_get_fragmentation(MemoryPool* p, FragmentStats* stats) {
    size_t count = 0, total = 0, largest = 0, smallest = (size_t)-1;
    for (FreeBlock* fb = p->free_list; fb; fb = fb->next) {
        count++;
        total += fb->size;
        if (fb->size > largest)   largest = fb->size;
        if (fb->size < smallest)  smallest = fb->size;
    }
    if (count == 0) smallest = 0;
    stats->num_fragments     = count;
    stats->total_free_bytes  = total;
    stats->largest_fragment  = largest;
    stats->smallest_fragment = smallest;
}
