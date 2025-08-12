# MemoryPool Library

Cross-language fixed-size buffer pools in C and Python for minimal allocation overhead and fragmentation.

## Overview

MemoryPool supplies a simple API to grab and return fixed-size buffers. Use it in C for systems code or in Python for prototyping and testing.

## Directory Structure

```
memory-pool
┣ 📂c
┃ ┣ 📜bench.exe
┃ ┣ 📜benchmark.c
┃ ┣ 📜main_smoketest.exe
┃ ┣ 📜main.c
┃ ┣ 📜pool.c
┃ ┗ 📜pool.h
┣ 📂data
┃ ┗ 📜results_python.csv
┣ 📂python
┃ ┣ 📂__pycache__
┃ ┃ ┣ 📜buffer_pool.cpython-313.pyc
┃ ┃ ┗ 📜test_buffer_pool.cpython-313.pyc
┃ ┣ 📜benchmark.py
┃ ┣ 📜buffer_pool.py
┃ ┗ 📜test_buffer_pool.py
┣ 📜LICENSE
┣ 📜make
┣ 📜README.md
┗ 📜requirements.txt
```

## Features

- O(1) alloc/free  
- Low internal fragmentation reporting  
- Thread-safety via optional build flag  
- Consistent API in both C and Python  

## Requirements

Install Python runtime dependencies:

```bash
pip install -r requirements.txt
```

## Building & Installation

### Prerequisites

- GCC  
- Make  
- Python 3.x and pip  

### Getting Started

```bash
git clone https://github.com/ishaan-1706/memory-pool
cd memorypool
```

#Replace the URL above with your repository’s clone link once it’s live.

### Build

```bash
make
```

This runs the C build in `c/` and installs Python dependencies.

### Smoke Test & Benchmark

```bash
./c/main_smoketest
./c/bench
```

### Install to Prefix

```bash
make install DESTDIR=/your/install/path
```

This installs:

- Binaries to `/your/install/path/usr/local/bin`  
- Header (`memorypool.h`) to `/your/install/path/usr/local/include`  

### Clean

```bash
make clean
```

## Quickstart

### C Example

```c
#include "memorypool.h"

int main() {
    Pool* pool = pool_init(1024, 1000);
    void* buf = pool_alloc(pool);
    // use buf…
    pool_free(pool, buf);
    printf("Fragmentation: %.2f%%\n", pool_get_fragmentation(pool));
    pool_destroy(pool);
    return 0;
}
```

Compile & run:

```bash
gcc -o demo demo.c -lmemorypool
./demo
```

### Python Example

```python
from memorypool import BufferPool

pool = BufferPool(buffer_size=1024, capacity=1000)
buf = pool.alloc()
# use buf…
pool.free(buf)
print(f"Fragmentation: {pool.get_fragmentation():.2f}%")
```

## Contributing

1. Fork the repo and create a feature branch.  
2. Commit your changes with clear messages.  
3. Open a pull request describing your feature or fix.  

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
