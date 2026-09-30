# [M] CVE-2025-32364

## Summary
Severity: Medium
Advisory: CVE-2025-32364
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-04-05
Source: https://osv.dev/vulnerability/CVE-2025-32364
Type: osv

## Details
A floating-point exception in the PSStack::roll function of Poppler before 25.04.0 can cause an application to crash when handling malformed inputs associated with INT_MIN.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00037.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32364.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32364
- https://gitlab.freedesktop.org/poppler/poppler/-/issues/1574
- https://gitlab.freedesktop.org/poppler/poppler/-/commit/d87bc726c7cc98f8c26b60ece5f20236e9de1bc3
