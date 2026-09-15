# [C] Cacti: Command Injection via escape_command() no-op in RRDtool execution

## Summary
Severity: Critical
Advisory: CVE-2026-40079
Aliases: GHSA-xq98-376r-hv9j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-40079
Type: osv

## Details
Cacti is an open source performance and fault management framework. Versions 1.2.30 and prior are vulnerable to Command Injection due to lack of sanitization in the escape_command() function. The escape_command() function at lib/rrd.php is a no-op: it returns $command unchanged. The command line built by rrdtool_function_graph() is passed through this function and then to shell_exec($full_commandline). The risk is in __rrd_execute() where text_format values from graph templates (which may contain host variable substitutions) reach shell_exec without adequate escaping. This issue has been addressed in version 1.2.31.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40079.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-xq98-376r-hv9j
- https://nvd.nist.gov/vuln/detail/CVE-2026-40079
- https://github.com/Cacti/cacti/commit/4c09efaebf3a9faec66969d0b5c4aceaf397f37f
