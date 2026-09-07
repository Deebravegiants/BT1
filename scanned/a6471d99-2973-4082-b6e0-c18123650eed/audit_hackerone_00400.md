# [H] Memory corrouption in mrb_gc_mark

## Summary
Severity: High (CVSS 7.3)
Program: shopify-scripts
Weakness: Memory Corruption - Generic
Reporter: minhrau
State: resolved
Disclosed: 2017-04-17T02:42:13.361Z
Source: https://hackerone.com/reports/208363

## Details
The memory corruption in mrb_gc_mark function can lead to code execution or at least DoS on mruby.

PoC attached.

### Crash debug

>mr@minhrau ~ $ ./mrubylatest/mruby/build/bench/bin/mruby ./mruby/fuzz03/crashes/mrb_gc_mark.rb
>Reading symbols from ./mrubylatest/mruby/build/bench/bin/mruby...done.
>(gdb) r ./mruby/fuzz03/crashes/mrb_gc_mark.rb
>Starting program: /home/minhrau/mrubylatest/mruby/build/bench/bin/mruby ./mruby/fuzz03/crashes/mrb_gc_mark.rb
>{:r=>["h1MuXist", "kenea", "mini[g", "\377\377\365"]}
>
>---snip---
>
>Program received signal SIGSEGV, Segmentation fault.
>mrb_gc_mark (obj=0x4b563330305c3035, mrb=0x69f010) at /home/minhrau/mrubylatest/mruby/src/gc.c:696
>696   if (!is_white(obj)) return;
>(gdb) p obj
>$1 = (struct RBasic *) 0x4b563330305c3035
>(gdb) x/i $rip
>=> 0x4185fe <incremental_gc+78>:    movzbl 0x1(%rax),%edx
>(gdb) i r
>rax            0x4b563330305c3035   5428582682904506421
>rbx            0x7422a0 7611040
>rcx            0x0  0
>rdx            0xffffffffffffffff   -1
>rsi            0x69f0e8 6942952
>rdi            0x69f010 6942736
>rbp            0xffffffffffffffff   0xffffffffffffffff
>rsp            0x7fffffffdc90   0x7fffffffdc90
>r8             0x4  4
>r9             0x6b2660 7022176
>r10            0x6b2650 7022160
>r11            0x7ffff73ea760   140737341466464
>r12            0x69f010 6942736
>r13            0x69f0e8 6942952
>r14            0x0  0
>r15            0x69f010 6942736

_Trimmed to 38 lines — full report: https://hackerone.com/reports/208363_
