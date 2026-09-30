# [H] CVE-2019-9544

## Summary
Severity: High
Advisory: CVE-2019-9544
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-01
Source: https://osv.dev/vulnerability/CVE-2019-9544
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-628. An out of bounds write occurs in AP4_CttsTableEntry::AP4_CttsTableEntry() located in Core/Ap4Array.h. It can be triggered by sending a crafted file to (for example) the mp42hls binary. It allows an attacker to cause Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- https://github.com/axiomatic-systems/Bento4/issues/374
- https://research.loginsoft.com/bugs/out-of-bounds-write-in-function-ap4_cttstableentryap4_cttstableentry-bento4-1-5-1-0/
