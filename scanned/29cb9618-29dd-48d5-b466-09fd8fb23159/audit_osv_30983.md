# [H] CVE-2024-57261

## Summary
Severity: High
Advisory: CVE-2024-57261
CVSS: 7.1 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2024-57261
Type: osv

## Details
In barebox before 2025.01.0, request2size in common/dlmalloc.c has an integer overflow, a related issue to CVE-2024-57258.

## References
- https://git.pengutronix.de/cgit/barebox/commit/?id=7cf25e0733f08f68d1bf0ca0c3cf6e2dfe51bd3c
- https://lists.infradead.org/pipermail/barebox/2024-November/048631.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57261.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57261
