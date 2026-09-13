# [C] pgadmin4 has a Meta-Command Filter Command Execution

## Summary
Severity: Critical
Advisory: GHSA-fxmw-jcgr-w44v
CVE: CVE-2025-13780
CWE: CWE-77, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2025-12-11
Source: https://github.com/advisories/GHSA-fxmw-jcgr-w44v
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.11

## Details
The PLAIN restore meta-command filter introduced in pgAdmin as part of the fix for CVE-2025-12762 does not detect meta-commands when a SQL file begins with a UTF-8 Byte Order Mark (EF BB BF) or other special byte sequences. The implemented filter uses the function `has_meta_commands()`, which scans raw bytes using a regular expression. The regex does not treat the bytes as ignorable, so meta-commands such as `\\!` remain undetected. When pgAdmin invokes psql with --file, psql strips the bytes and executes the command. This can result in remote command execution during a restore operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13780
- https://github.com/pgadmin-org/pgadmin4/issues/9368
- https://github.com/pgadmin-org/pgadmin4/pull/9426
- https://github.com/pgadmin-org/pgadmin4/commit/1d397395f75320ca1d4ed5e9ca721c603415e836
- https://github.com/pgadmin-org/pgadmin4/commit/d5a909f14cb9713d89b49481ad1929fad89f4576
- https://github.com/pgadmin-org/pgadmin4
