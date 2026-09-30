# [H] LimeSurvey is vulnerable to SQL injection

## Summary
Severity: High
Advisory: GHSA-rccq-2fxq-7x3h
CVE: CVE-2025-56421
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-rccq-2fxq-7x3h
Type: github-advisory

## Affected
- Packagist: `limesurvey/limesurvey` — affected >=0 <6.15.4

## Details
SQL Injection vulnerability in LimeSurvey before v.6.15.4+250710 allows a remote attacker to obtain sensitive information from the database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56421
- https://github.com/LimeSurvey/LimeSurvey/pull/4328
- https://github.com/LimeSurvey/LimeSurvey/commit/d6c3c780cdd17d5eef1c8c69ad0105beffa2374f
- https://github.com/LimeSurvey/LimeSurvey
- https://github.com/hongancalif/security-advisories/blob/main/CVE-2025-56421.md
- http://limesurvey.com
