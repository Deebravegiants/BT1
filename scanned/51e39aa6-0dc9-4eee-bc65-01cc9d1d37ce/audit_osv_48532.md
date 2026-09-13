# [M] CVE-2017-9083

## Summary
Severity: Medium
Advisory: CVE-2017-9083
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-19
Source: https://osv.dev/vulnerability/CVE-2017-9083
Type: osv

## Details
poppler 0.54.0, as used in Evince and other products, has a NULL pointer dereference in the JPXStream::readUByte function in JPXStream.cc. For example, the perf_test utility will crash (segmentation fault) when parsing an invalid PDF file.

## References
- https://security.gentoo.org/glsa/201801-17
- https://bugs.freedesktop.org/show_bug.cgi?id=101084
