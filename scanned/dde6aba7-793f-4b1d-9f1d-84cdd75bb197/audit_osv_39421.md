# [H] Dokploy: Command Injection via incomplete shell escaping in docker logout (registry deletion)

## Summary
Severity: High
Advisory: CVE-2026-45662
Aliases: GHSA-827c-7x62-29jq
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45662
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In 0.29.0 and earlier, the deleteRegistry function in Dokploy (packages/server/src/services/registry.ts) executes docker logout ${response.registryUrl} without shell escaping. In the same file, the docker login command correctly uses shEscape() to prevent command injection. This inconsistency creates a command injection vulnerability when deleting a registry with a crafted registryUrl.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45662.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-827c-7x62-29jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-45662
