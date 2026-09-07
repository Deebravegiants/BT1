# [M] admidio CSRF Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c4v8-2hg8-jv77
CVE: CVE-2017-8382
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-c4v8-2hg8-jv77
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <4.1-Beta.1

## Details
admidio 3.2.8 has CSRF in `adm_program/modules/members/members_function.php` with an impact of deleting arbitrary user accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8382
- https://github.com/Admidio/admidio/issues/612
- https://github.com/Admidio/admidio/pull/1074
- https://github.com/Admidio/admidio/commit/a7ac9d3c9e0780e877fe9ac846ac64b284de8553
- https://github.com/Admidio/admidio
- https://github.com/faizzaidi/Admidio-3.2.8-CSRF-POC-by-Provensec-llc
- https://www.exploit-db.com/exploits/42005
- http://en.0day.today/exploit/27771
