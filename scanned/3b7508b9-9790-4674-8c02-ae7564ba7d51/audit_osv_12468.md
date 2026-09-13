# [H] CVE-2018-12321

## Summary
Severity: High
Advisory: CVE-2018-12321
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-12321
Type: osv

## Details
There is a heap out of bounds read in radare2 2.6.0 in java_switch_op() in libr/anal/p/anal_java.c via a crafted Java binary file.

## References
- https://github.com/radare/radare2/issues/10296
- https://github.com/radare/radare2/commit/224e6bc13fa353dd3b7f7a2334588f1c4229e58d
