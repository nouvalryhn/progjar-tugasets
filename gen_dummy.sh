#!/bin/bash

# Membuat file 10MB, 50MB, 100MB
dd if=/dev/urandom of=dummy_10MB.bin bs=1M count=10
dd if=/dev/urandom of=dummy_50MB.bin bs=1M count=50
dd if=/dev/urandom of=dummy_100MB.bin bs=1M count=100