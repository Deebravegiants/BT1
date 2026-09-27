# [M] CVE-2026-56132

## Summary
Severity: Medium
Advisory: CVE-2026-56132
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-56132
Type: osv

## Details
In libexpat before 2.8.2, there is a heap-based buffer overflow in doProlog in xmlparse.c because scaffold backing array reallocation is mishandled when there is data-structure sharing across parsers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56132.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56132
- https://github.com/libexpat/libexpat/pull/1272
