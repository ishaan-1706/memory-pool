import unittest
from buffer_pool import BufferPool, FragmentStats

class TestBufferPool(unittest.TestCase):
    def test_alloc_free_basic(self):
        # Initialize pool of 1 KiB
        pool_size = 1024
        pool = BufferPool(pool_size)

        # Allocate two blocks
        ptr1 = pool.alloc(128)
        ptr2 = pool.alloc(256)
        self.assertIsInstance(ptr1, int)
        self.assertIsInstance(ptr2, int)

        # Free them
        pool.free(ptr1, 128)
        pool.free(ptr2, 256)

        # Check fragmentation: should reclaim entire pool
        frag = pool.get_fragmentation()
        self.assertEqual(frag.num_fragments, 1)
        self.assertEqual(frag.total_free, pool_size)
        self.assertEqual(frag.largest, pool_size)
        self.assertEqual(frag.smallest, pool_size)

    def test_over_allocate_raises(self):
        pool = BufferPool(512)
        with self.assertRaises(MemoryError):
            pool.alloc(1024)

if __name__ == '__main__':
    unittest.main()
