# [M] Karapace: Path Traversal in Backup Reader

## Summary
Severity: Medium
Advisory: CVE-2026-29190
Aliases: GHSA-rw4j-p3jg-4fxq
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-29190
Type: osv

## Details
Karapace is an open-source implementation of Kafka REST and Schema Registry. Prior to version 6.0.0, there is a Path Traversal vulnerability in the backup reader (backup/backends/v3/backend.py). If a malicious backup file is provided to Karapace, an attacker may exploit insufficient path validation to perform arbitrary file read on the system where Karapace is running. The issue affects deployments that use the backup/restore functionality and process backups from untrusted sources. The impact depends on the file system permissions of the Karapace process. This issue has been patched in version 6.0.0.

## References
- https://github.com/Aiven-Open/karapace/releases/tag/6.0.0
- https://github.com/Aiven-Open/karapace/security/advisories/GHSA-rw4j-p3jg-4fxq
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29190.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29190
