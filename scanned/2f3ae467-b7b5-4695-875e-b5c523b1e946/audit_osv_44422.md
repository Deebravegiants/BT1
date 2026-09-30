# [H] Duplicacy Path Traversal during Restore via Unsanitized Snapshot Paths

## Summary
Severity: High
Advisory: CVE-2026-82264
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82264
Type: osv

## Details
Duplicacy through 3.2.5 contains a path traversal vulnerability in the restore function that fails to validate entry paths deserialized from snapshot files. Attackers can craft malicious snapshot entries with directory traversal sequences to write files outside the restore directory to arbitrary locations accessible by the restoring user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82264.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82264
- https://www.vulncheck.com/advisories/duplicacy-path-traversal-during-restore-via-unsanitized-snapshot-paths
- https://github.com/gilbertchen/duplicacy/issues/692
- https://github.com/gilbertchen/duplicacy
- https://github.com/gilbertchen/duplicacy/blob/54f97522bff9df8be6797873203310ccbf5a5b00/src/duplicacy_backupmanager.go
- https://github.com/gilbertchen/duplicacy/blob/54f97522bff9df8be6797873203310ccbf5a5b00/src/duplicacy_utils_others.go
