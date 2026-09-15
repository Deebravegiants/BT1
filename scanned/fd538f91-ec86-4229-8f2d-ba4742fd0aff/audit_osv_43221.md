# [C] Dokploy: OS Command Injection via dockerImage field in database service deployment functions → HOST RCE

## Summary
Severity: Critical
Advisory: CVE-2026-72862
Aliases: GHSA-6jrh-8qmg-jj3p
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72862
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the mariadb.ts, mongo.ts, mysql.ts, postgres.ts, redis.ts, and libsql.ts Dokploy database service deployment functions pass user-controlled dockerImage fields unquoted into docker pull ${dockerImage} shell commands on the remote-server code path. This vulnerability is fixed in 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72862.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-6jrh-8qmg-jj3p
- https://nvd.nist.gov/vuln/detail/CVE-2026-72862
- https://github.com/Dokploy/dokploy/commit/b24202e69b244f0ece8d2f56e99cad9bb5e1a248
