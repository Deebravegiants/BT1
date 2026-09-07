# [H] ThinkPHP deserialization vulnerability

## Summary
Severity: High
Advisory: GHSA-pjhx-j53p-c5f5
CVE: CVE-2024-48112
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-30
Source: https://github.com/advisories/GHSA-pjhx-j53p-c5f5
Type: github-advisory

## Affected
- Packagist: `topthink/thinkphp` — affected >=6.1.3

## Details
A deserialization vulnerability in the component \controller\Index.php of Thinkphp v6.1.3 to v8.0.4 allows attackers to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48112
- https://github.com/nn0nkey/nn0nkey/blob/main/Thinkphp/CVE-2024-48112.md
- https://github.com/top-think/think
