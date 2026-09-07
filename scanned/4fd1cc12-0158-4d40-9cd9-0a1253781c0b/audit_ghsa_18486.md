# [H] Bacula-web SQL Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-hq25-vp56-qr86
CVE: CVE-2025-45346
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-29
Source: https://github.com/advisories/GHSA-hq25-vp56-qr86
Type: github-advisory

## Affected
- Packagist: `bacula-web/bacula-web` — affected >=0 <9.7.1

## Details
SQL Injection vulnerability in Bacula-web before v.9.7.1 allows a remote attacker to execute arbitrary code via a crafted HTTP GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-45346
- https://github.com/bacula-web/bacula-web/commit/ad5d94809f17994a61496ecfec9cd3a16ac14a5f
- https://github.com/bacula-web/bacula-web
- https://github.com/bacula-web/bacula-web/releases/tag/v9.7.1
