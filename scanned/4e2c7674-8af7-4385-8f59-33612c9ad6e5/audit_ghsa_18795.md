# [H] sqls-server/sqls is vulnerable to command injection in the config command 

## Summary
Severity: High
Advisory: GHSA-f9f4-5859-29mf
CVE: CVE-2025-61141
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-10-30
Source: https://github.com/advisories/GHSA-f9f4-5859-29mf
Type: github-advisory

## Affected
- Go: `github.com/sqls-server/sqls` — affected 0.2.28

## Details
sqls-server/sqls 0.2.28 is vulnerable to command injection in the config command because the openEditor function passes the EDITOR environment variable and config file path to sh -c without sanitization, allowing attackers to execute arbitrary commands.

This issue has been patched via commit https://github.com/sqls-server/sqls/commit/468a23fc89af89f632cc023a10c031e4bc781797.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61141
- https://github.com/sqls-server/sqls/commit/468a23fc89af89f632cc023a10c031e4bc781797
- https://advisory.dw1.io/54
- https://github.com/sqls-server/sqls
- https://lukmanern.github.io/CVE-2025-61141.html
- https://pkg.go.dev/vuln/GO-2025-4088
