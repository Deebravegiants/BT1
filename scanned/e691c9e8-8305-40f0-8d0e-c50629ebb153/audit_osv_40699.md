# [H] Broken Access Control in Azuriom CMS Server Routes Allows Account Takeover

## Summary
Severity: High
Advisory: CVE-2026-54415
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-54415
Type: osv

## Details
Missing Authorization in the server management routes (routes/admin.php) in Azuriom Azuriom CMS before 1.2.11 on all platforms allows an authenticated attacker with the admin.access permission to create AzLink server tokens and take over non-admin user accounts by changing their passwords and email addresses via crafted HTTP requests to /admin/servers/create and the AzLink API endpoints (/api/azlink/password, /api/azlink/email, /api/azlink/user/{id}).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54415.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54415
- https://github.com/Azuriom/Azuriom/commit/4b744bc0dd11f205f5aa053c6db8a949d3f0608e
- https://github.com/Azuriom/Azuriom/releases/tag/v1.2.11
- https://github.com/Azuriom/Azuriom
