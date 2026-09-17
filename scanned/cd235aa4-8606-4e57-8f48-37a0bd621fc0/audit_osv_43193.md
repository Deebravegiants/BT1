# [C] Dokploy: Cross-organization IDOR in Dokploy backup destinations exposes another tenant's S3 credentials and backups

## Summary
Severity: Critical
Advisory: CVE-2026-72737
Aliases: GHSA-56qv-89fq-3h2q
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72737
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In 0.29.8 and earlier, backup.create, backup.update, and backup.restoreBackupWithLogs in apps/dokploy/server/api/routers/backup.ts accept a client-controlled destinationId and use the referenced destination without verifying that destination.organizationId equals ctx.session.activeOrganizationId. An authenticated member with backup permissions for a service in one organization can cause another organization's S3 accessKey and secretAccessKey to be materialized by packages/server/src/utils/backups/utils.ts getS3Credentials on the attacker's service host, read that organization's backup objects, or redirect and poison backups across tenant boundaries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72737.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-56qv-89fq-3h2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-72737
