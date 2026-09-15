# [H] CVE-2017-14164

## Summary
Severity: High
Advisory: CVE-2017-14164
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-06
Source: https://osv.dev/vulnerability/CVE-2017-14164
Type: osv

## Details
A size-validation issue was discovered in opj_j2k_write_sot in lib/openjp2/j2k.c in OpenJPEG 2.2.0. The vulnerability causes an out-of-bounds write, which may lead to remote denial of service (heap-based buffer overflow affecting opj_write_bytes_LE in lib/openjp2/cio.c) or possibly remote code execution. NOTE: this vulnerability exists because of an incomplete fix for CVE-2017-14152.

## References
- http://www.securityfocus.com/bid/100677
- https://security.gentoo.org/glsa/201710-26
- https://blogs.gentoo.org/ago/2017/09/06/heap-based-buffer-overflow-in-opj_write_bytes_le-cio-c-incomplete-fix-for-cve-2017-14152/
- https://github.com/uclouvain/openjpeg/commit/dcac91b8c72f743bda7dbfa9032356bc8110098a
- https://github.com/uclouvain/openjpeg/issues/991
