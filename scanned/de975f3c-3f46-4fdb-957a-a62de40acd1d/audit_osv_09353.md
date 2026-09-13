# [M] CVE-2016-9572

## Summary
Severity: Medium
Advisory: CVE-2016-9572
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-9572
Type: osv

## Details
A NULL pointer dereference flaw was found in the way openjpeg 2.1.2 decoded certain input images. Due to a logic error in the code responsible for decoding the input image, an application using openjpeg to process image data could crash when processing a crafted image.

## References
- http://www.securityfocus.com/bid/109233
- https://security.gentoo.org/glsa/201710-26
- https://www.debian.org/security/2017/dsa-3768
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9572
- https://github.com/szukw000/openjpeg/commit/7b28bd2b723df6be09fe7791eba33147c1c47d0d
- https://github.com/uclouvain/openjpeg/issues/863
