# [H] CVE-2025-51463

## Summary
Severity: High
Advisory: CVE-2025-51463
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-51463
Type: osv

## Details
Path Traversal in restore_run_backup() in AIM 3.28.0 allows remote attackers to write arbitrary files to the server's filesystem via a crafted backup tar file submitted to the run_instruction API, which is extracted without path validation during restoration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51463.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51463
- https://github.com/aimhubio/aim/pull/3327
- https://github.com/aimhubio/aim
- https://www.gecko.security/blog/cve-2025-51463
