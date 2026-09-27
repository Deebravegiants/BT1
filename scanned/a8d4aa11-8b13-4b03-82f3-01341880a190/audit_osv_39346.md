# [C] MyBooks: Privilege Escalation via Missing Authorization on Admin Settings Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-45273
Aliases: GHSA-354j-9hx8-3p45
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-45273
Type: osv

## Details
MyBooks is an ebook management web server also known as Talebook. In 3.41.2 and earlier, the AdminSettings.post handler for POST /api/admin/settings in webserver/handlers/admin.py applies the auth decorator but does not check the self.admin_user property, unlike the corresponding GET handler. Any authenticated regular user can therefore overwrite server configuration values including SMTP credentials, OAuth client secrets, storage paths, security feature flags, and autoreload settings. The process_auth_header function in webserver/handlers/base.py also fails to verify the matched account's active flag, allowing a registered but unactivated account to authenticate and reach the vulnerable handler. Exploitation can disclose secrets through configuration access paths, sabotage application behavior, force service restarts, and supply the settings needed for related code-injection attacks. This issue is fixed in version 3.42.0.

## References
- https://github.com/PoxenStudio/mybooks/releases/tag/3.42.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45273.json
- https://github.com/PoxenStudio/mybooks/security/advisories/GHSA-354j-9hx8-3p45
- https://nvd.nist.gov/vuln/detail/CVE-2026-45273
- https://github.com/PoxenStudio/mybooks/commit/a1780c98b00566af7da2fc099fe38500efc02e92
