# [M] VictoriaMetrics vmrestore: path traversal via crafted backup part names escapes restore root

## Summary
Severity: Medium
Advisory: CVE-2026-61625
Aliases: GHSA-8q3c-rjr9-xxrp
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-61625
Type: osv

## Details
VictoriaMetrics is a scalable solution for monitoring and managing time series data. Prior to 1.122.25, 1.136.12, and 1.146.0, vmrestore does not validate backup part path components before using lib/backup/actions/restore.go and lib/backup/fslocal/fslocal.go to write restored data below storageDataPath. An attacker who can supply or modify an S3, GCS, Azure Blob Storage, or other backup source can place .. components in object names. When an operator restores that source, the crafted names can create or overwrite files outside the intended restore root within the filesystem permissions of the vmrestore process. This issue is fixed in versions 1.122.25, 1.136.12, and 1.146.0.

## References
- https://github.com/VictoriaMetrics/VictoriaMetrics/releases/tag/v1.122.25
- https://github.com/VictoriaMetrics/VictoriaMetrics/releases/tag/v1.136.12
- https://github.com/VictoriaMetrics/VictoriaMetrics/releases/tag/v1.146.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61625.json
- https://github.com/VictoriaMetrics/VictoriaMetrics/security/advisories/GHSA-8q3c-rjr9-xxrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-61625
- https://github.com/VictoriaMetrics/VictoriaMetrics/commit/710c920d6083327042a309e449fae4383617d817
