# [C] CyberPanel IncBackups IDOR via Sequential Backup ID

## Summary
Severity: Critical
Advisory: CVE-2026-65917
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65917
Type: osv

## Details
CyberPanel through 1.9.1, fixed in commit b198460, contains an insecure direct object reference (IDOR) vulnerability in the IncBackups application's incremental-backup handlers (deleteBackup, fetchRestorePoints, and restorePoint) that allows authenticated panel users to access or manipulate other tenants' backup resources by supplying an attacker-controlled globally sequential IncJob integer ID that is never re-scoped to the authorized domain. Attackers can enumerate sequential backup IDs to read another tenant's backup metadata, irrecoverably delete another tenant's backup snapshots, or trigger unauthorized restoration of another tenant's backup job with root privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65917.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65917
- https://www.vulncheck.com/advisories/cyberpanel-incbackups-idor-via-sequential-backup-id
- https://github.com/usmannasir/cyberpanel/issues/1828
- https://github.com/usmannasir/cyberpanel/commit/b1984603f9b0099b39bca46fea176e53b6d4d601
- https://github.com/usmannasir/cyberpanel
