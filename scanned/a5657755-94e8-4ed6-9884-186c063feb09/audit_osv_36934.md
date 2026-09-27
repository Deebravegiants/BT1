# [C] Dokploy has Command Injection in its Service Operations

## Summary
Severity: Critical
Advisory: CVE-2026-27130
Aliases: GHSA-fcgq-jjfg-hrhj
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-27130
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Versions 0.26.6 and below have OS command injection through the appName parameter. 3 chained issues cause this problem: inadequate input sanitization, lack of schema validation and direct shell interpolation. User-controlled application names are passed through inadequate sanitization (cleanAppName function only replaces spaces and converts to lowercase) before being interpolated directly into shell commands executed via execAsync() and execAsyncRemote(). An authenticated attacker can inject shell metacharacters (e.g., ;, $(), backticks, |, &) in the appName field during application creation, which are then executed with server-level privileges when service operations (start, stop, remove, scale) are triggered. This issue has been resolved in version 0.26.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27130.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-fcgq-jjfg-hrhj
- https://nvd.nist.gov/vuln/detail/CVE-2026-27130
- https://github.com/Dokploy/dokploy/commit/960892fd8dcf12b7a73a00edaa1b7090fca860c7
