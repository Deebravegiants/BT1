# [M] CVE-2019-6988

## Summary
Severity: Medium
Advisory: CVE-2019-6988
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-28
Source: https://osv.dev/vulnerability/CVE-2019-6988
Type: osv

## Details
An issue was discovered in OpenJPEG 2.3.0. It allows remote attackers to cause a denial of service (attempted excessive memory allocation) in opj_calloc in openjp2/opj_malloc.c, when called from opj_tcd_init_tile in openjp2/tcd.c, as demonstrated by the 64-bit opj_decompress.

## References
- http://www.securityfocus.com/bid/106785
- https://github.com/uclouvain/openjpeg/issues/1178
