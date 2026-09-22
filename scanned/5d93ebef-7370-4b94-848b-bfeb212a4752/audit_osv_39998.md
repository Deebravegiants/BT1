# [H] Apache Answer: Denial of service via crafted Accept-Language header parsing

## Summary
Severity: High
Advisory: CVE-2026-48834
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-48834
Type: osv

## Details
Improper Handling of Length Parameter Inconsistency vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.1.

Unauthenticated attackers can cause a denial of service via a specially crafted Accept-Language header that triggers excessive CPU consumption during parsing.
Users are recommended to upgrade to version 2.0.2, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/05/9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48834.json
- https://lists.apache.org/thread/0yg5smwnbrhqs55m5h61gn42mcs8s95p
- https://nvd.nist.gov/vuln/detail/CVE-2026-48834
