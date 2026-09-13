# [M] Microweber vulnerable to command injection

## Summary
Severity: Medium
Advisory: GHSA-582p-2fpg-x226
CVE: CVE-2023-1877
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-582p-2fpg-x226
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.3.3

## Details
microweber/microweber prior to 1.3.3 is vulnerable to command injection in the "first name" field. This allows for server-side template injection, which can lead to arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1877
- https://github.com/microweber/microweber/commit/93a906d0bf096c3ab1674012a90c88d101e76c8d
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/71fe4b3b-20ac-448c-8191-7b99d7ffaf55
