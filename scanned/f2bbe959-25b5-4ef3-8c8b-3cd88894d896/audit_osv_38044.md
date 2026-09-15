# [M] himmelblau: NSS fake-primary group lookup reintroduces name collision risk

## Summary
Severity: Medium
Advisory: CVE-2026-34397
Aliases: GHSA-v7xx-7mqc-g835
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-34397
Type: osv

## Details
Himmelblau is an interoperability suite for Microsoft Azure Entra ID and Intune. From versions 2.0.0-alpha to before 2.3.9 and 3.0.0-alpha to before 3.1.1, there is a conditional local privilege escalation vulnerability in an edge-case naming collision. Only authenticated himmelblau users whose mapped CN/short name exactly matches a privileged local group name (e.g., "sudo", "wheel", "docker", "adm") can cause the NSS module to resolve that group name to their fake primary group. If the system uses NSS results for group-based authorization decisions (sudo, polkit, etc.), this can grant the attacker the privileges of that group. This issue has been patched in versions 2.3.9 and 3.1.1.

## References
- https://github.com/himmelblau-idm/himmelblau/releases/tag/2.3.9
- https://github.com/himmelblau-idm/himmelblau/releases/tag/3.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34397.json
- https://github.com/himmelblau-idm/himmelblau/security/advisories/GHSA-v7xx-7mqc-g835
- https://nvd.nist.gov/vuln/detail/CVE-2026-34397
