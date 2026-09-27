# [H] CVE-2019-9656

## Summary
Severity: High
Advisory: CVE-2019-9656
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-11
Source: https://osv.dev/vulnerability/CVE-2019-9656
Type: osv

## Details
An issue was discovered in LibOFX 0.9.14. There is a NULL pointer dereference in the function OFXApplication::startElement in the file lib/ofx_sgml.cpp, as demonstrated by ofxdump.

## References
- https://github.com/libofx/libofx/issues/22
- https://lists.debian.org/debian-lts-announce/2019/11/msg00021.html
- https://usn.ubuntu.com/4523-1/
- https://github.com/TeamSeri0us/pocs/tree/master/libofx
