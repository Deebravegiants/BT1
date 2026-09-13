# [H] Centreon SQL Injection vulnerability via esc_name parameter

## Summary
Severity: High
Advisory: GHSA-25gv-wg6f-6frp
CVE: CVE-2022-40043
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-27
Source: https://github.com/advisories/GHSA-25gv-wg6f-6frp
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <21.04.16
- Packagist: `centreon/centreon` — affected >=21.10.0 <21.10.8
- Packagist: `centreon/centreon` — affected >=22.0.0 <22.04.2

## Details
Centreon v20.10.18 was discovered to contain a SQL injection vulnerability via the `esc_name` (Escalation Name) parameter at `Configuration/Notifications/Escalations`. Versions 21.04.16, 21.10.8, and 22.04.2 contain patches.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40043
- https://github.com/centreon/centreon/commit/1a6ee0e9a003ac4f07dc8c370aec6e8911279358
- https://github.com/centreon/centreon/commit/76fdfba312515656419a1311a83adfb11a73199f
- https://github.com/centreon/centreon/commit/cee5d3b0b0077182dfced5fb1d216a4ac168c05f
- https://github.com/centreon/centreon
- https://github.com/centreon/centreon/releases
- https://www.hakaioffensivesecurity.com/centreon-sqli-and-xss-vulnerability
