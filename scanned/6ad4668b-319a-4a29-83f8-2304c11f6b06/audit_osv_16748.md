# [H] CVE-2019-9543

## Summary
Severity: High
Advisory: CVE-2019-9543
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-01
Source: https://osv.dev/vulnerability/CVE-2019-9543
Type: osv

## Details
An issue was discovered in Poppler 0.74.0. A recursive function call, in JBIG2Stream::readGenericBitmap() located in JBIG2Stream.cc, can be triggered by sending a crafted pdf file to (for example) the pdfseparate binary. It allows an attacker to cause Denial of Service (Segmentation fault) or possibly have unspecified other impact. This is related to JArithmeticDecoder::decodeBit.

## References
- http://www.securityfocus.com/bid/107238
- https://research.loginsoft.com/bugs/recursive-function-call-in-function-jbig2streamreadgenericbitmap-poppler-0-74-0/
- https://gitlab.freedesktop.org/poppler/poppler/issues/730
