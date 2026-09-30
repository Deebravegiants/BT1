# [M] CVE-2025-32365

## Summary
Severity: Medium
Advisory: CVE-2025-32365
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-04-05
Source: https://osv.dev/vulnerability/CVE-2025-32365
Type: osv

## Details
Poppler before 25.04.0 allows crafted input files to trigger out-of-bounds reads in the JBIG2Bitmap::combine function in JBIG2Stream.cc because of a misplaced isOk check.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00037.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32365.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32365
- https://gitlab.freedesktop.org/poppler/poppler/-/issues/1577
- https://gitlab.freedesktop.org/poppler/poppler/-/merge_requests/1792
