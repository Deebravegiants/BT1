# [M] n8n before 1.123.69 Code Node Sandbox Escape via Function.prototype Pollution

## Summary
Severity: Medium
Advisory: CVE-2026-77083
Aliases: GHSA-c9c6-rq46-h25v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77083
Type: osv

## Details
n8n is a workflow automation platform. In versions prior to 1.123.69, 2.33.4, and 2.34.1, the JavaScript Code node's VM sandbox did not freeze the sandbox's Function.prototype, allowing an authenticated user with the ability to create and execute workflows to pollute it from within a Code node execution and recover a reference to the host's globalThis, resulting in a sandbox escape. The full exploit chain additionally depends on specific modules being available as allowlisted imports in the deployment's configuration. The issue is fixed in versions 1.123.69, 2.33.4, and 2.34.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77083.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-c9c6-rq46-h25v
- https://nvd.nist.gov/vuln/detail/CVE-2026-77083
- https://www.vulncheck.com/advisories/n8n-before-code-node-sandbox-escape-via-function.prototype-pollution
