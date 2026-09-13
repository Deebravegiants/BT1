# [H] CyberPanel Missing Authorization in cancelBackupCreation Handler

## Summary
Severity: High
Advisory: CVE-2026-65916
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65916
Type: osv

## Details
CyberPanel through 1.9.1, fixed in commit b198460, contains a missing authorization vulnerability in the cancelBackupCreation handler that allows authenticated users to kill, delete, and corrupt other tenants' backups. Attackers can send crafted POST requests with arbitrary backupCancellationDomain and fileName parameters to terminate backup processes, delete backup archives, corrupt backup status files, and remove database records belonging to other tenants.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65916.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65916
- https://www.vulncheck.com/advisories/cyberpanel-missing-authorization-in-cancelbackupcreation-handler
- https://github.com/usmannasir/cyberpanel/issues/1829
- https://github.com/usmannasir/cyberpanel/commit/b1984603f9b0099b39bca46fea176e53b6d4d601
- https://github.com/usmannasir/cyberpanel
