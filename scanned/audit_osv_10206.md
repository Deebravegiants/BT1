# [H] CVE-2017-14258

## Summary
Severity: High
Advisory: CVE-2017-14258
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-11
Source: https://osv.dev/vulnerability/CVE-2017-14258
Type: osv

## Details
In the SDK in Bento4 1.5.0-616, SetItemCount in Core/Ap4StscAtom.h file contains a Write Memory Access Violation vulnerability. It is possible to exploit this vulnerability and possibly execute arbitrary code by opening a crafted .MP4 file.

## References
- https://github.com/axiomatic-systems/Bento4/issues/181
