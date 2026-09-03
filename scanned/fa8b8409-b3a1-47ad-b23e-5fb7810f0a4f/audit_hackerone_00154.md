# [H] Heap buffer overflow vulnerability while processing a malformed TIFF file.

## Summary
Severity: High (CVSS 8.6)
Program: Internet Bug Bounty
Weakness: Heap Overflow
Reporter: hardik05
State: resolved
Disclosed: 2021-07-09T20:21:02.894Z
CVE: CVE-2020-27829
Source: https://hackerone.com/reports/1047086

## Details
A heap buffer overflow vulnerability occurs in magick while processing of a malformed TIFF file.Following is the version/build details:
```
$ magick -version
Version: ImageMagick 7.0.10-45 Q16 x86_64 2020-11-30 https://imagemagick.org
Copyright: © 1999-2020 ImageMagick Studio LLC
License: https://imagemagick.org/script/license.php
Features: Cipher DPC HDRI OpenMP(4.5)
Delegates (built-in): freetype jbig jng jpeg lcms lzma png raw tiff webp x zlib
```

Replication details:
1. run following command with attached poc.tif file:
```
magick poc.tif /dev/null
```
note: zip file password is infected.

you should see the crash as mentioned below.

Following is the crash details:
```
=21316==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x6110000004f8 at pc 0x5638f9a55850 bp 0x7fffc92d67b0 sp 0x7fffc92d67a0
READ of size 1 at 0x6110000004f8 thread T0
    #0 0x5638f9a5584f in PushQuantumPixel MagickCore/quantum-import.c:256
    #1 0x5638f9a5584f in ImportRGBQuantum MagickCore/quantum-import.c:4105
    #2 0x5638f9b13e3d in ImportQuantumPixels MagickCore/quantum-import.c:4775
    #3 0x5638f82186f4 in ReadTIFFImage coders/tiff.c:2025
    #4 0x5638f8720e14 in ReadImage MagickCore/constitute.c:563
    #5 0x5638f872e40c in ReadImages MagickCore/constitute.c:953
    #6 0x5638fb49c996 in CLINoImageOperator MagickWand/operation.c:4853
    #7 0x5638fb4aae31 in CLIOption MagickWand/operation.c:5350
    #8 0x5638fae155ca in ProcessCommandOptions MagickWand/magick-cli.c:424
    #9 0x5638fae1ec23 in MagickImageCommand MagickWand/magick-cli.c:796
    #10 0x5638fae26a0e in MagickCommandGenesis MagickWand/mogrify.c:191
    #11 0x5638f63ddab5 in MagickMain utilities/magick.c:149
    #12 0x7f5d91238bf6 in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x21bf6)
    #13 0x5638f63da6e9 in _start (/usr/local/bin/magick+0x20f26e9)

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1047086_
