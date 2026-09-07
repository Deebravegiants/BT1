# [M] ThinkCMF Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4847-gqxx-v9xp
CVE: CVE-2020-25915
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-4847-gqxx-v9xp
Type: github-advisory

## Affected
- Packagist: `thinkcmf/thinkcmf` — affected >=0 <5.1.7

## Details
Cross Site Scripting (XSS) vulnerability in `UserController.php` in ThinkCMF version 5.1.5, allows attackers to execute arbitrary code via crafted `user_login`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25915
- https://github.com/thinkcmf/thinkcmf/issues/675
- https://github.com/thinkcmf/thinkcmf/commit/27e1fbea5aed5619d15c1257614df45298f04436
- https://github.com/thinkcmf/thinkcmf
