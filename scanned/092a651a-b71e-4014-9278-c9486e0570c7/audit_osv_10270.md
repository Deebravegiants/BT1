# [M] CVE-2017-14643

## Summary
Severity: Medium
Advisory: CVE-2017-14643
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14643
Type: osv

## Details
The AP4_HdlrAtom class in Core/Ap4HdlrAtom.cpp in Bento4 version 1.5.0-617 uses an incorrect character data type, leading to a heap-based buffer over-read and application crash in AP4_BytesToUInt32BE in Core/Ap4Utils.h.

## References
- https://blogs.gentoo.org/ago/2017/09/14/bento4-heap-based-buffer-overflow-in-ap4_bytestouint32be-ap4utils-h/
- https://github.com/axiomatic-systems/Bento4/commit/5eb8cf89d724ccb0b4ce5f24171ec7c11f0a7647
- https://github.com/axiomatic-systems/Bento4/issues/187
