# [H] BillaBear is Vulnerable to SQL Injection in the EventRepository

## Summary
Severity: High
Advisory: GHSA-xp6r-8pcc-xv5p
CVE: CVE-2026-31069
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-xp6r-8pcc-xv5p
Type: github-advisory

## Affected
- Packagist: `billabear/billabear` — affected >=0

## Details
BillaBear (all versions prior to Jan 2026) contains a SQL Injection vulnerability in the EventRepository. User-controlled input from metric filter names and aggregation properties is directly interpolated into SQL queries using sprintf() without proper sanitization or identifier quoting. Although filter values are parameterized, the filter identifiers (keys) are not. An authenticated attacker with ROLE_ACCOUNT_MANAGER permissions can exploit this to execute arbitrary SQL commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31069
- https://gist.github.com/nedlir/2377ba6e7fa2ad957210b52aa8e400d9
- https://gist.github.com/nedlir/a50725b94650467f0593b8f4009ae19e
- https://github.com/billabear/billabear
