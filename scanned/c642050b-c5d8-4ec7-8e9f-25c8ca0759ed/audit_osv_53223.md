# [M] CVE-2022-34266

## Summary
Severity: Medium
Advisory: CVE-2022-34266
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-07-19
Source: https://osv.dev/vulnerability/CVE-2022-34266
Type: osv

## Details
The libtiff-4.0.3-35.amzn2.0.1 package for LibTIFF on Amazon Linux 2 allows attackers to cause a denial of service (application crash), a different vulnerability than CVE-2022-0562. When processing a malicious TIFF file, an invalid range may be passed as an argument to the memset() function within TIFFFetchStripThing() in tif_dirread.c. This will cause TIFFFetchStripThing() to segfault after use of an uninitialized resource.

## References
- https://alas.aws.amazon.com/AL2/ALAS-2022-1814.html
- https://bugs.gentoo.org/859433
