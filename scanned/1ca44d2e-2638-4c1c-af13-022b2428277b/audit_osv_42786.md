# [H] Fledge IoT Gateway Backup Restore OS Command Injection via Tar Member Filename

## Summary
Severity: High
Advisory: CVE-2026-71284
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71284
Type: osv

## Details
Fledge's backup-restore upload handler, upload_backup (python/fledge/services/core/api/backup_restore.py), takes the first extracted tar member's filename (tar_file_names[0]) and builds a shell command via string formatting. Because os.system invokes a shell and no quoting (shlex.quote, list-form subprocess) is applied, an admin uploading a crafted backup archive achieves arbitrary OS command execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71284.json
- https://github.com/fledge-iot/fledge
- https://github.com/fledge-iot/fledge/blob/main/python/fledge/services/core/api/backup_restore.py
- https://nvd.nist.gov/vuln/detail/CVE-2026-71284
