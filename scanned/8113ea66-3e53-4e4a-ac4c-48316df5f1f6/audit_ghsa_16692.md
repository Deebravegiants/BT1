# [C] Mocodo vulnerable to SQL injection in `/web/generate.php`

## Summary
Severity: Critical
Advisory: GHSA-j6cv-98jx-mrwr
CVE: CVE-2024-35374
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-j6cv-98jx-mrwr
Type: github-advisory

## Affected
- PyPI: `mocodo` — affected >=0 <4.2.7

## Details
Mocodo Mocodo Online 4.2.6 and below does not properly sanitize the `sql_case` input field in `/web/generate.php`, allowing remote attackers to execute arbitrary SQL commands and potentially command injection, leading to remote code execution (RCE) under certain conditions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-35374
- https://github.com/laowantong/mocodo/commit/f9368df28518b6c4a92fd207c260f1978ec34d6e
- https://chocapikk.com/posts/2024/mocodo-vulnerabilities
- https://github.com/laowantong/mocodo
- https://github.com/laowantong/mocodo/blob/11ca879060a68e06844058cd969c6379214cc2a8/web/generate.php#L104-L158
