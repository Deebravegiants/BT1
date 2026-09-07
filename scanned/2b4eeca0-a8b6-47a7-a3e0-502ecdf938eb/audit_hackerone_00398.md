# [M] Use of uninitialized memory in unserialize()

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Code Injection
Reporter: rc0r
State: resolved
Disclosed: 2017-06-01T18:41:51.251Z
CVE: CVE-2017-5340
Source: https://hackerone.com/reports/195950

## Details
The following is a copy of the bug report at https://bugs.php.net/bug.php?id=73832

# Description

There was found a bug showing that PHP uses uninitialized memory during
calls to `unserialize()`. As the following report shows, the payload supplied
to `unserialize()` may control this uninitialized memory region and thus may
be used to trick PHP into operating on faked objects and calling attacker
controlled destructor function pointers. The supplied proof of concept exploit
practically demonstrates the issue by executing arbitrary code solely by
passing a specially crafted string to `unserialize()`. Even though this
particular demo exploit only works locally this flaw is very likely to also
allow for remote code execution.

This bug was found using `afl-fuzz` / `afl-utils`.


# Analysis

The following shows a short gdb dump of the flaw in a custom-built PHP (git
master on 40727d7ce9) with debugging symbols ([1], [2]):

    $ gdb ./sapi/cli/php
    gdb> r test.php payload.master
    [...]
    Fatal error: Possible integer overflow in memory allocation (2736264714 * 32 + 32) in test.php on line 6

    Program received signal SIGSEGV, Segmentation fault.
    gdb> i r
    rax            0x7ffff7fb673c	140737353836348
    rbx            0x3030303030303030	3472328296227680304
    rcx            0xf6d9	63193
    rdx            0x1cb8c30	30116912
    rsi            0x0	0
    rdi            0x3030303030303030	3472328296227680304
    rbp            0x30303030	0x30303030
    rsp            0x7fffffffc080	0x7fffffffc080
    r8             0x7ffff7fb6740	140737353836352

_Trimmed to 38 lines — full report: https://hackerone.com/reports/195950_
