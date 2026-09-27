# [H] WWBN AVideo Improper Restriction of Excessive Authentication Attempts vulnerability

## Summary
Severity: High
Advisory: GHSA-v977-h4hm-rrff
CVE: CVE-2023-49810
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-v977-h4hm-rrff
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
A login attempt restriction bypass vulnerability exists in the checkLoginAttempts functionality of WWBN AVideo dev master commit 15fed957fb. A specially crafted HTTP request can lead to captcha bypass, which can be abused by an attacker to bruteforce users credentials. An attacker can send a series of HTTP requests to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49810
- https://github.com/WWBN/AVideo/commit/15fed957fb64b4055158acfc449bd7974346edb5
- https://github.com/WWBN/AVideo
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1898
