# [C] Dokploy allows attackers to  run arbitrary OS commands on the Dokploy host.

## Summary
Severity: Critical
Advisory: CVE-2025-53376
Aliases: GHSA-m486-7pmj-8cmv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-53376
Type: osv

## Details
Dokploy is a self-hostable Platform as a Service (PaaS) that simplifies the deployment and management of applications and databases. An authenticated, low-privileged user can run arbitrary OS commands on the Dokploy host. The tRPC procedure
docker.getContainersByAppNameMatch interpolates the attacker-supplied appName value into a Docker CLI call without sanitisation, enabling command injection under the Dokploy service account. This vulnerability is fixed in 0.23.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53376.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-m486-7pmj-8cmv
- https://nvd.nist.gov/vuln/detail/CVE-2025-53376
- https://github.com/Dokploy/dokploy/commit/fb5d2bd5b67322f1468e5e4d0d5abcf97517761c
