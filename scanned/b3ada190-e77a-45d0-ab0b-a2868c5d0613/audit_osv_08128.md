# [M] CVE-2016-10507

## Summary
Severity: Medium
Advisory: CVE-2016-10507
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2016-10507
Type: osv

## Details
Integer overflow vulnerability in the bmp24toimage function in convertbmp.c in OpenJPEG before 2.2.0 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted bmp file.

## References
- http://www.securityfocus.com/bid/100567
- https://security.gentoo.org/glsa/201710-26
- https://github.com/uclouvain/openjpeg/commit/da940424816e11d624362ce080bc026adffa26e8
- https://github.com/uclouvain/openjpeg/issues/833
