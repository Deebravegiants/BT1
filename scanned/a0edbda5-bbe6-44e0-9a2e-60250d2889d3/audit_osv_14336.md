# [M] CVE-2018-9145

## Summary
Severity: Medium
Advisory: CVE-2018-9145
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-30
Source: https://osv.dev/vulnerability/CVE-2018-9145
Type: osv

## Details
In the DataBuf class in include/exiv2/types.hpp in Exiv2 0.26, an issue exists in the constructor with an initial buffer size. A large size value may lead to a SIGABRT during an attempt at memory allocation. NOTE: some third parties have been unable to reproduce the SIGABRT when using the 4-DataBuf-abort-1 PoC file.

## References
- https://security.gentoo.org/glsa/201811-14
- https://bugzilla.novell.com/show_bug.cgi?id=1087879
- https://bugzilla.redhat.com/show_bug.cgi?id=1564281
- https://github.com/xiaoqx/pocs/tree/master/exiv2
