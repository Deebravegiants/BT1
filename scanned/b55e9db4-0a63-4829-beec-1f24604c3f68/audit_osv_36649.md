# [H] Dokploy uses hardcoded credentials in installation script, which could result in database access

## Summary
Severity: High
Advisory: CVE-2026-24840
Aliases: GHSA-jr65-3j3w-gjmc
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24840
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In versions prior to 0.26.6, a hardcoded credential in the provided installation script (located at https://dokploy.com/install.sh, line 154) uses a hardcoded password when creating the database container. This means that nearly all Dokploy installations use the same database credentials and could be compromised. Version 0.26.6 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24840.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-jr65-3j3w-gjmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-24840
- https://github.com/Dokploy/dokploy/commit/b902c160a256ad345ac687c87eb092f1fab2c64d
