# [H] CVE-2018-14585

## Summary
Severity: High
Advisory: CVE-2018-14585
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-24
Source: https://osv.dev/vulnerability/CVE-2018-14585
Type: osv

## Details
An issue has been discovered in Bento4 1.5.1-624. AP4_BytesToUInt16BE in Core/Ap4Utils.h has a heap-based buffer over-read after a call from the AP4_Stz2Atom class.

## References
- https://github.com/axiomatic-systems/Bento4/issues/299
