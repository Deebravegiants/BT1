# [H] CVE-2017-14259

## Summary
Severity: High
Advisory: CVE-2017-14259
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-11
Source: https://osv.dev/vulnerability/CVE-2017-14259
Type: osv

## Details
In the SDK in Bento4 1.5.0-616, the AP4_StscAtom class in Ap4StscAtom.cpp contains a Write Memory Access Violation vulnerability. It is possible to exploit this vulnerability and possibly execute arbitrary code by opening a crafted .MP4 file.

## References
- https://github.com/axiomatic-systems/Bento4/issues/181
