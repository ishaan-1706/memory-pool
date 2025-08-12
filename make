# Makefile at project root

# Directory containing your C code
C_DIR := c

.PHONY: all build build-c install clean

# Default: install Python deps and build C
all: build python-deps

# Build C targets
build-c:
    $(MAKE) -C $(C_DIR)

# Install Python dependencies
python-deps:
    pip install -r requirements.txt

# Alias for building everything
build: build-c python-deps

# Delegate install to C/Makefile
install:
    $(MAKE) -C $(C_DIR) install DESTDIR=$(DESTDIR)

# Clean C artifacts
clean:
    $(MAKE) -C $(C_DIR) clean
