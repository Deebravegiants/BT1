# [M] CVE-2017-12982

## Summary
Severity: Medium
Advisory: CVE-2017-12982
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-21
Source: https://osv.dev/vulnerability/CVE-2017-12982
Type: osv

## Details
The bmp_read_info_header function in bin/jp2/convertbmp.c in OpenJPEG 2.2.0 does not reject headers with a zero biBitCount, which allows remote attackers to cause a denial of service (memory allocation failure) in the opj_image_create function in lib/openjp2/image.c, related to the opj_aligned_alloc_n function in opj_malloc.c.

## References
- https://security.gentoo.org/glsa/201710-26
- https://blogs.gentoo.org/ago/2017/08/14/openjpeg-memory-allocation-failure-in-opj_aligned_alloc_n-opj_malloc-c/
- https://github.com/uclouvain/openjpeg/commit/baf0c1ad4572daa89caa3b12985bdd93530f0dd7
- https://github.com/uclouvain/openjpeg/issues/983
