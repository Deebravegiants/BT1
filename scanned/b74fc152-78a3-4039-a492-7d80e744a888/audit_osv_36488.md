# [C] Blinko: Admin RCE - MCP Server Command Injection

## Summary
Severity: Critical
Advisory: CVE-2026-23882
Aliases: GHSA-59r2-82p8-c56v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-23882
Type: osv

## Details
Blinko is an AI-powered card note-taking project. Prior to version 1.8.4, the MCP (Model Context Protocol) server creation function allows specifying arbitrary commands and arguments, which are executed when testing the connection. This issue has been patched in version 1.8.4.

## References
- https://github.com/blinkospace/blinko/releases/tag/1.8.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23882.json
- https://github.com/blinkospace/blinko/security/advisories/GHSA-59r2-82p8-c56v
- https://nvd.nist.gov/vuln/detail/CVE-2026-23882
- https://github.com/blinkospace/blinko/commit/bef6b770743e87c630db2d00d7049dabd96bfe85
