# [H] Velociraptor VQL injection during notebook restore from backup

## Summary
Severity: High
Advisory: CVE-2026-19584
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-19584
Type: osv

## Details
Velociraptor allows for the creation of notebook backups in its default enabled daily backup feature. When Velociraptor restores the backup, the notebook cell content is interpolated into a template with no ACL checks. This allows a malicious user with NOTEBOOK_EDITOR permission to plant a VQL query which will be evaluated at elevated permissions if the notebook's backup is subsequently restored.

## References
- http://docs.velociraptor.app/announcements/advisories/cve-2026-19584/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19584.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19584
- https://github.com/Velocidex/velociraptor/pull/4967
- https://github.com/Velocidex/velociraptor
