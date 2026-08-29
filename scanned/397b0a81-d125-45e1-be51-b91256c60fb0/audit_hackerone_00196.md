# [H] null pointer dereference in imap_mail

## Summary
Severity: High (CVSS 7.5)
Program: Internet Bug Bounty
Weakness: Out-of-bounds Read
Reporter: shuoz
State: resolved
Disclosed: 2020-11-09T01:45:05.229Z
CVE: CVE-2018-19935
Source: https://hackerone.com/reports/456727

## Details
in imap_mail if message args is null, in _php_imap_mail no check wheater message  can get, so crash.

```
     fprintf(sendmail, "\n%s\n", message);

```



/usr/local/php/bin/php ./craxxx.php 

Warning: imap_mail(): No message string in mail command in /home/fan/github/php-7.2.10/myselffuzz/craxxx.php on line 3
sh: 1: -t: not found
Segmentation fault (core dumped)







../sapi/cli/php ./craxxx.php 

Warning: imap_mail(): No message string in mail command in /home/fan/github/php-7.2.10/myselffuzz/craxxx.php on line 3
ASAN:SIGSEGV
=================================================================
==23766==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000018 (pc 0x7fae925d9cc0 bp 0x7ffcb6b27a10 sp 0x7ffcb6b274a0 T0)
sh: 1: -t: not found
    #0 0x7fae925d9cbf in vfprintf (/lib/x86_64-linux-gnu/libc.so.6+0x4ecbf)
    #1 0x7fae926a1bc8 in __fprintf_chk (/lib/x86_64-linux-gnu/libc.so.6+0x116bc8)
    #2 0xa5aeb0 in fprintf /usr/include/x86_64-linux-gnu/bits/stdio2.h:97
    #3 0xa5aeb0 in _php_imap_mail /home/fan/github/php-7.2.10/ext/imap/php_imap.c:4065
    #4 0xa5b22d in zif_imap_mail /home/fan/github/php-7.2.10/ext/imap/php_imap.c:4112
    #5 0x17da703 in ZEND_DO_ICALL_SPEC_RETVAL_UNUSED_HANDLER /home/fan/Desktop/php-7.2.10/Zend/zend_vm_execute.h:573
    #6 0x17da703 in execute_ex /home/fan/Desktop/php-7.2.10/Zend/zend_vm_execute.h:59747
    #7 0x181b5c3 in zend_execute /home/fan/Desktop/php-7.2.10/Zend/zend_vm_execute.h:63776
    #8 0x1356ef2 in zend_execute_scripts /home/fan/Desktop/php-7.2.10/Zend/zend.c:1496
    #9 0x11c0776 in php_execute_script /home/fan/Desktop/php-7.2.10/main/main.c:2590

_Trimmed to 38 lines — full report: https://hackerone.com/reports/456727_
