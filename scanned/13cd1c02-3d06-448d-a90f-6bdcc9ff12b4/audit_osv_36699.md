# [C] Group-Office Argument Injection in MaintenanceController::actionZipLanguage

## Summary
Severity: Critical
Advisory: CVE-2026-25134
Aliases: GHSA-v39j-549w-8849
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-02
Source: https://osv.dev/vulnerability/CVE-2026-25134
Type: osv

## Details
Group-Office is an enterprise customer relationship management and groupware tool. Prior to 6.8.150, 25.0.82, and 26.0.5, the MaintenanceController exposes an action zipLanguage which takes a lang parameter and passes it directly to a system zip command via exec(). This can be combined with uploading a crafted zip file to achieve remote code execution. This vulnerability is fixed in 6.8.150, 25.0.82, and 26.0.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25134.json
- https://github.com/Intermesh/groupoffice/security/advisories/GHSA-v39j-549w-8849
- https://nvd.nist.gov/vuln/detail/CVE-2026-25134
- https://github.com/Intermesh/groupoffice/commit/d28490a6a29936db7888aa841ab8ade88800540b
