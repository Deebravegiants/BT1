# [H] CVE-2016-9573

## Summary
Severity: High
Advisory: CVE-2016-9573
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-9573
Type: osv

## Details
An out-of-bounds read vulnerability was found in OpenJPEG 2.1.2, in the j2k_to_image tool. Converting a specially crafted JPEG2000 file to another format could cause the application to crash or, potentially, disclose some data from the heap.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0838.html
- http://www.securityfocus.com/bid/97073
- https://security.gentoo.org/glsa/201710-26
- https://www.debian.org/security/2017/dsa-3768
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9573
- https://github.com/szukw000/openjpeg/commit/7b28bd2b723df6be09fe7791eba33147c1c47d0d
- https://github.com/uclouvain/openjpeg/issues/862
