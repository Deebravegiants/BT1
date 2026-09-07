# [H] MantisBT: SQL Injection via history_order Configuration Value

## Summary
Severity: High
Advisory: GHSA-mw6p-33vw-46cc
CVE: CVE-2026-47142
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-mw6p-33vw-46cc
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.4

## Details
MantisBT 2.28.3 and earlier versions contains a SQL injection vulnerability in core/history_api.php. The history_order configuration value is concatenated directly into a SQL ORDER BY clause without any sanitisation, parameterization, or validation against a whitelist.

An administrator can set this configuration value via the web UI (adm_config_set.php) or the REST API (PATCH /api/rest/config). The injected SQL then executes whenever any user views a bug with history entries.

### Impact
- Sensitive data extraction from the entire bugtracker database including user credentials (cookie_string, password hashes), API tokens, and private issue data
- With MySQL FILE privilege: full RCE via INTO OUTFILE writing a PHP webshell to the web root
- The admin plants the payload once; any authenticated user viewing a bug with history triggers the injection

### Patches
- https://github.com/mantisbt/mantisbt/commit/6ad20bea2e01f33c6e4170775ae4d9dbe2c75325

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### Resources
- https://mantisbt.org/bugs/view.php?id=37123

### Credits
McCaulay Hudson (@McCaulay) of watchTowr

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-mw6p-33vw-46cc
- https://github.com/mantisbt/mantisbt/commit/6ad20bea2e01f33c6e4170775ae4d9dbe2c75325
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37123
