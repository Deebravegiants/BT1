# [C] Dokploy: Member-role RCE as host root via destination.testConnection rclone shell injection

## Summary
Severity: Critical
Advisory: CVE-2026-72868
Aliases: GHSA-f6x8-vfwh-8hjr
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72868
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, apps/dokploy/server/api/routers/destination.ts interpolates the accessKey, secretAccessKey, region, endpoint, provider, and bucket fields from destination.testConnection into an rclone ls command executed through child_process.exec. The `withPermission("destination", "create")` path permits a low-privileged organization member to reach the mutation, close a quoted argument with a crafted field, and execute arbitrary commands in the root Dokploy container, which has access to the host Docker socket. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72868.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-f6x8-vfwh-8hjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-72868
- https://github.com/Dokploy/dokploy/commit/eeb6e7b8ea88e4b4b1fac8460755464100516ac9
- https://github.com/Dokploy/dokploy/pull/4873
