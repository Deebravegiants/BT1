# [M] CVE-2020-21674

## Summary
Severity: Medium
Advisory: CVE-2020-21674
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-10-15
Source: https://osv.dev/vulnerability/CVE-2020-21674
Type: osv

## Details
Heap-based buffer overflow in archive_string_append_from_wcs() (archive_string.c) in libarchive-3.4.1dev allows remote attackers to cause a denial of service (out-of-bounds write in heap memory resulting into a crash) via a crafted archive file. NOTE: this only affects users who downloaded the development code from GitHub. Users of the product's official releases are unaffected.

## References
- https://github.com/libarchive/libarchive/issues/1298
- https://github.com/libarchive/libarchive/commit/4f085eea879e2be745f4d9bf57e8513ae48157f4
