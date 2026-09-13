# [M] n8n before 1.123.69 Remote Code Execution via EventEmitter Prototype Pollution

## Summary
Severity: Medium
Advisory: CVE-2026-77077
Aliases: GHSA-m3hg-p5r9-fg9h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77077
Type: osv

## Details
n8n versions before 1.123.69, 2.33.4, and 2.34.1 contain a JavaScript task runner VM sandbox escape. The runner's prototype-freezing routine covers globalThis functions but not internal module constructors such as EventEmitter, allowing an authenticated user with Code node access to exploit prototype pollution to execute arbitrary commands within the runner container. Because the polluted prototype is a process-wide object, the corruption persists across other tenants' Code node executions on the same shared runner. On v1.x instances without task runners enabled, Code node JavaScript runs directly in the main n8n process, where the impact could be higher.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77077.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-m3hg-p5r9-fg9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-77077
- https://www.vulncheck.com/advisories/n8n-before-remote-code-execution-via-eventemitter-prototype-pollution
