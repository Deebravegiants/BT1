# [C] Coolify: WebSocket Endpoint Access Control Flaw Leading to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-34047
Aliases: GHSA-652w-qv22-2r7c
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34047
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, terminal WebSocket bootstrap routes did not enforce the expected authorization middleware, allowing an authenticated user to access terminal functionality for resources outside the authorized scope and potentially execute commands. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34047.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-652w-qv22-2r7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-34047
- https://github.com/coollabsio/coolify/commit/bc91b41f92f1bbb53886a5d7a60335cbf1621cd5
- https://github.com/coollabsio/coolify/pull/9169
