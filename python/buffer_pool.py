import os
import psutil
import threading

class FragmentStats:
    def __init__(self, num_fragments, total_free, largest, smallest):
        self.num_fragments = num_fragments
        self.total_free = total_free
        self.largest = largest
        self.smallest = smallest

class BufferPool:
    def __init__(self, total_bytes):
        self._lock = threading.Lock()
        self._buffer = bytearray(total_bytes)
        # free_list holds (offset, length)
        self._free_list = [(0, total_bytes)]

    def alloc(self, size):
        size = ((size + 7) // 8) * 8
        with self._lock:
            for i, (off, length) in enumerate(self._free_list):
                if length >= size:
                    ptr = off
                    rem = length - size
                    if rem:
                        self._free_list[i] = (off + size, rem)
                    else:
                        self._free_list.pop(i)
                    return ptr
            raise MemoryError("BufferPool out of memory")

    def free(self, ptr, size):
        with self._lock:
            self._free_list.append((ptr, size))
            # optional: coalesce adjacent blocks
            self._free_list = self._coalesce(self._free_list)

    def _coalesce(self, free_list):
        free_list = sorted(free_list, key=lambda x: x[0])
        merged = []
        for off, length in free_list:
            if merged and merged[-1][0] + merged[-1][1] == off:
                prev_off, prev_len = merged.pop()
                merged.append((prev_off, prev_len + length))
            else:
                merged.append((off, length))
        return merged

    def get_fragmentation(self):
        with self._lock:
            if not self._free_list:
                return FragmentStats(0, 0, 0, 0)
            lengths = [l for _, l in self._free_list]
            return FragmentStats(
                num_fragments=len(lengths),
                total_free=sum(lengths),
                largest=max(lengths),
                smallest=min(lengths)
            )
