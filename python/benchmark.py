# python/benchmark.py

import os
import random
import time
import psutil
import csv

from buffer_pool import BufferPool

# Toggle DEBUG for quick local runs
DEBUG    = True
NUM_OPS  = 20_000 if DEBUG else 100_000
MIN_SIZE = 16
MAX_SIZE = 256

BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RESULTS_CSV = os.path.join(BASE_DIR, 'data', 'results_python.csv')


def get_rss_kb():
    return psutil.Process().memory_info().rss // 1024


def bench_malloc():
    ptrs = []
    for i in range(NUM_OPS):
        if i and i % (NUM_OPS // 5) == 0:
            print(f"  [malloc] {i:6d} / {NUM_OPS} allocations done")
        size = random.randint(MIN_SIZE, MAX_SIZE)
        ptrs.append(bytearray(size))
    return ptrs


def bench_pool(pool):
    ptrs = []
    for i in range(NUM_OPS):
        if i and i % (NUM_OPS // 5) == 0:
            print(f"  [pool]   {i:6d} / {NUM_OPS} allocations done")
        size = random.randint(MIN_SIZE, MAX_SIZE)
        off = pool.alloc(size)
        ptrs.append((off, size))
    return ptrs


def batch_merge_fragmentation(ptrs):
    """
    Implements the batch-free + one-pass merge approach:
      1. Gather all (offset, offset+size) segments
      2. Sort by offset
      3. Merge adjacent segments in one pass
      4. Compute fragmentation stats in O(n)
    Returns: (num_fragments, total_free, largest, smallest, times)
    """
    t0 = time.perf_counter()

    # 1. Gather segments
    segments = [(off, off + size) for off, size in ptrs]
    t1 = time.perf_counter()

    # 2. Sort by start offset
    segments.sort(key=lambda seg: seg[0])
    t2 = time.perf_counter()

    # 3. One‐pass merge
    merged = []
    for start, end in segments:
        if merged and merged[-1][1] == start:
            # extend the last segment
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    t3 = time.perf_counter()

    # 4. Compute stats
    sizes = [end - start for start, end in merged]
    num_frag    = len(merged)
    total_free  = sum(sizes)
    largest     = max(sizes) if sizes else 0
    smallest    = min(sizes) if sizes else 0
    t4 = time.perf_counter()

    times = {
        'gather_ms':  (t1 - t0) * 1000,
        'sort_ms':    (t2 - t1) * 1000,
        'merge_ms':   (t3 - t2) * 1000,
        'stats_ms':   (t4 - t3) * 1000,
        'total_ms':   (t4 - t0) * 1000,
    }

    return num_frag, total_free, largest, smallest, times


def run():
    print(f"Starting benchmark with {NUM_OPS} ops (DEBUG={DEBUG})\n")
    random.seed(0)

    # Phase 1: malloc/free
    print("Phase 1: malloc/free")
    t0 = time.perf_counter()
    ptrs = bench_malloc()
    t1 = time.perf_counter()
    rss1 = get_rss_kb()
    print(f"  malloc/free done in {(t1 - t0)*1000:.2f} ms, RSS = {rss1} KB\n")
    del ptrs

    # Phase 2: buffer‐pool alloc
    print("Phase 2: buffer-pool alloc")
    pool = BufferPool(NUM_OPS * MAX_SIZE)
    t2 = time.perf_counter()
    ptrs = bench_pool(pool)
    t3 = time.perf_counter()
    rss2 = get_rss_kb()
    print(f"  pool alloc done in {(t3 - t2)*1000:.2f} ms, RSS = {rss2} KB\n")

    # Phase 3: batch‐free + one‐pass merge fragmentation
    print("Phase 3: batch-free + one-pass merge fragmentation stats")
    num_frag, total_free, largest, smallest, times = batch_merge_fragmentation(ptrs)
    print(f"  Gather segments: {times['gather_ms']:.2f} ms")
    print(f"  Sort segments:   {times['sort_ms']:.2f} ms")
    print(f"  Merge segments:  {times['merge_ms']:.2f} ms")
    print(f"  Compute stats:   {times['stats_ms']:.2f} ms")
    print(f"  Total Phase 3:   {times['total_ms']:.2f} ms")
    print(f"  Fragments={num_frag}, total_free={total_free} B, largest={largest} B, smallest={smallest} B\n")

    # Phase 4: write CSV
    print(f"Phase 4: writing results to {RESULTS_CSV}")
    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    with open(RESULTS_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "mode","time_ms","rss_kb",
            "num_fragments","total_free_b","largest_b","smallest_b"
        ])
        writer.writerow([
            "malloc", (t1 - t0) * 1000, rss1,
            "N/A","N/A","N/A","N/A"
        ])
        writer.writerow([
            "pool",   (t3 - t2) * 1000, rss2,
            num_frag, total_free, largest, smallest
        ])

    print("\nBenchmark complete.")


if __name__ == "__main__":
    run()
