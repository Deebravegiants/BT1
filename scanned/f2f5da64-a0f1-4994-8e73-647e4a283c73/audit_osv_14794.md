# [M] CVE-2019-11463

## Summary
Severity: Medium
Advisory: CVE-2019-11463
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2019-11463
Type: osv

## Details
A memory leak in archive_read_format_zip_cleanup in archive_read_support_format_zip.c in libarchive 3.3.4-dev allows remote attackers to cause a denial of service via a crafted ZIP file because of a HAVE_LZMA_H typo. NOTE: this only affects users who downloaded the development code from GitHub. Users of the product's official releases are unaffected.

## References
- https://access.redhat.com/security/cve/cve-2019-11463
- https://github.com/libarchive/libarchive/commit/ba641f73f3d758d9032b3f0e5597a9c6e593a505
- https://github.com/libarchive/libarchive/issues/1165
