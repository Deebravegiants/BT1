# [M] alerta-server has potential SQL Injection vulnerability in Query String Syntax (q=) API

## Summary
Severity: Medium
Advisory: GHSA-8prr-286p-4w7j
CVE: CVE-2026-34400
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-8prr-286p-4w7j
Type: github-advisory

## Affected
- PyPI: `alerta-server` — affected >=0 <9.1.0

## Details
### Impact
The Query string search API (q=) was vulnerable to SQL injection via the Postgres query parser, which built WHERE clauses by interpolating user-supplied search terms directly into SQL strings via f-strings.

### Patches
Fixed in v9.1.0. The Postgres query parser now uses parameterized queries with %(name)s placeholders passed to psycopg2's cursor.execute(), preventing SQL injection through the ?q= parameter. The MongoDB backend was not affected.

### Workarounds
Upgrade to v9.1.0 or later. If unable to upgrade, deploy a proxy in front of the Alerta API to sanitize the q= parameter.

### Resources
https://github.com/alerta/alerta/pull/712/files
https://owasp.org/www-community/attacks/SQL_Injection

## References
- https://github.com/alerta/alerta/security/advisories/GHSA-8prr-286p-4w7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-34400
- https://github.com/alerta/alerta/pull/2040
- https://github.com/alerta/alerta/pull/712
- https://github.com/alerta/alerta/commit/aeba85a37a09e5769a7a2da56481aa979ff99a00
- https://github.com/alerta/alerta/commit/fdd52cd1abad8d02d1dfb8ecdcdbb43b6af3b883
- https://github.com/alerta/alerta
- https://github.com/alerta/alerta/releases/tag/v9.1.0
