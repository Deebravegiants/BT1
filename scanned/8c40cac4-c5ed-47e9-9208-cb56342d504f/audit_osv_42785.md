# [M] Fledge IoT Gateway Backup Restore Tar Path Traversal

## Summary
Severity: Medium
Advisory: CVE-2026-71283
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71283
Type: osv

## Details
Fledge's backup-restore upload handler, upload_backup (python/fledge/services/core/api/backup_restore.py), calls tarfile.extractall(temp_path) on an admin-uploaded tar archive with no filter argument and no per-member path validation. Requires the admin role (@has_permission("admin")).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71283.json
- https://github.com/fledge-iot/fledge
- https://github.com/fledge-iot/fledge/blob/main/python/fledge/services/core/api/backup_restore.py
- https://nvd.nist.gov/vuln/detail/CVE-2026-71283
