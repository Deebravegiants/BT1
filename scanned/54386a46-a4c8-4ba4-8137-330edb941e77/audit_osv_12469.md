# [M] CVE-2018-12322

## Summary
Severity: Medium
Advisory: CVE-2018-12322
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-12322
Type: osv

## Details
There is a heap out of bounds read in radare2 2.6.0 in _6502_op() in libr/anal/p/anal_6502.c via a crafted iNES ROM binary file.

## References
- https://github.com/radare/radare2/issues/10294
- https://github.com/radare/radare2/commit/bbb4af56003c1afdad67af0c4339267ca38b1017
