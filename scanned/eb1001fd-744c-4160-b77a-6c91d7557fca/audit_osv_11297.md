# [M] CVE-2017-7275

## Summary
Severity: Medium
Advisory: CVE-2017-7275
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2017-7275
Type: osv

## Details
The ReadPCXImage function in coders/pcx.c in ImageMagick 7.0.4.9 allows remote attackers to cause a denial of service (attempted large memory allocation and application crash) via a crafted file. NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-8862 and CVE-2016-8866.

## References
- http://www.securityfocus.com/bid/97166
- https://blogs.gentoo.org/ago/2017/03/27/imagemagick-memory-allocation-failure-in-acquiremagickmemory-memory-c-incomplete-fix-for-cve-2016-8862-and-cve-2016-8866/
- https://github.com/ImageMagick/ImageMagick/issues/271
