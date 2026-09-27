# [C] Lara Dashboard before 1.3.2 Incorrect Authorization in Core-Upgrade Archive Upload

## Summary
Severity: Critical
Advisory: CVE-2026-86437
Aliases: GHSA-xv98-x5h7-4g7v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86437
Type: osv

## Details
Lara Dashboard before 1.3.2 authorizes the POST /admin/settings/core-upgrades/upload endpoint with only the settings.edit permission, allowing non-Superadmin administrators to upload and extract arbitrary zip archives over the live application source code. Attackers can upload a malicious archive containing modified application files such as routes/web.php with embedded system commands, which execute as the web server user with access to environment secrets and database credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86437.json
- https://github.com/laradashboard/laradashboard/releases/tag/v1.3.2
- https://github.com/laradashboard/laradashboard/security/advisories/GHSA-xv98-x5h7-4g7v
- https://nvd.nist.gov/vuln/detail/CVE-2026-86437
- https://www.vulncheck.com/advisories/lara-dashboard-before-1.3.2-incorrect-authorization-in-core-upgrade-archive-upload
- https://github.com/laradashboard/laradashboard/commit/738cc1a219ce459323ef1d09c3789075f1b8d2f2
- https://github.com/laradashboard/laradashboard
- https://github.com/laradashboard/laradashboard/blob/v1.3.1/app/Http/Requests/CoreUpgrade/UploadRequest.php#L15-L18
- https://github.com/laradashboard/laradashboard/blob/v1.3.1/app/Policies/SettingPolicy.php#L47-L50
- https://github.com/laradashboard/laradashboard/blob/v1.3.1/app/Services/CoreUpgradeService.php#L543-L577
