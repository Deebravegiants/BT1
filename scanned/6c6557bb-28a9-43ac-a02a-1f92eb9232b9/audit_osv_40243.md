# [H] CVE-2026-52492

## Summary
Severity: High
Advisory: CVE-2026-52492
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-52492
Type: osv

## Details
An integer overflow in the libtiff rgb2ycbcr utility's cvtRaster() function when computing strip buffer sizes can result in an undersized heap allocation and subsequent heap-based buffer overflow during YCbCr conversion of a crafted TIFF image

## References
- https://gist.github.com/okyfh/fbc5a37cade358361d80f6a498560cfa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52492.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52492
- https://gitlab.com/libtiff/libtiff/-/commit/94affc5cf54111312f9891eb77accb93eebc28d7
