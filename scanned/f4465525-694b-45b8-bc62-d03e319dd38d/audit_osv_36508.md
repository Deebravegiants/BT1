# [H] Arcane allows unauthenticated proxy access to remote environments

## Summary
Severity: High
Advisory: CVE-2026-23944
Aliases: GHSA-2jv8-39rp-cqqr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23944
Type: osv

## Details
Arcane is an interface for managing Docker containers, images, networks, and volumes. Prior to version 1.13.2, unauthenticated requests could be proxied to remote environment agents, allowing access to remote environment resources without authentication. The environment proxy middleware handled `/api/environments/{id}/...` requests for remote environments before authentication was enforced. When the environment ID was not local, the middleware proxied the request and attached the manager-held agent token, even if the caller was unauthenticated. This enabled unauthenticated access to remote environment operations (e.g., listing containers, streaming logs, or other agent endpoints). An unauthenticated attacker could access and manipulate remote environment resources via the proxy, potentially leading to data exposure, unauthorized changes, or service disruption. Version 1.13.2 patches the vulnerability.

## References
- https://github.com/getarcaneapp/arcane/releases/tag/v1.13.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23944.json
- https://github.com/getarcaneapp/arcane/security/advisories/GHSA-2jv8-39rp-cqqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-23944
- https://github.com/getarcaneapp/arcane/commit/2008e1b93b25d0c4c3fff3af07843766231614eb
- https://github.com/getarcaneapp/arcane/pull/1532
