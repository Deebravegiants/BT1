# [M] Dokploy allows attackers to read any file that the Traefik process user can access

## Summary
Severity: Medium
Advisory: CVE-2025-53375
Aliases: GHSA-vq94-qm94-mxp6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-53375
Type: osv

## Details
Dokploy is a self-hostable Platform as a Service (PaaS) that simplifies the deployment and management of applications and databases. An authenticated attacker can read any file that the Traefik process user can access (e.g., /etc/passwd, application source, environment variable files containing credentials and secrets). This may lead to full compromise of other services or lateral movement. This vulnerability is fixed in 0.23.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53375.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-vq94-qm94-mxp6
- https://nvd.nist.gov/vuln/detail/CVE-2025-53375
- https://github.com/Dokploy/dokploy/commit/e42f6bc61050cd438726921fced64477cbf8f8e6
