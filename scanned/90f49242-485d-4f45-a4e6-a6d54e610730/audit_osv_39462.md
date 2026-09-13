# [M] Dokploy: Password Change Does Not Revoke Active Sessions

## Summary
Severity: Medium
Advisory: CVE-2026-45791
Aliases: GHSA-rr9m-w87g-46f3
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-45791
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.6, Dokploy's user.update procedure in apps/dokploy/server/api/routers/user.ts updates account.password without deleting other rows from session, allowing a compromised better-auth.session_token session to remain valid for up to three days after a password change. This issue is fixed in version 0.29.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45791.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-rr9m-w87g-46f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-45791
- https://github.com/Dokploy/dokploy/commit/a07106d649991ea09892220873ea3243766c3e08
- https://github.com/Dokploy/dokploy/pull/4475
