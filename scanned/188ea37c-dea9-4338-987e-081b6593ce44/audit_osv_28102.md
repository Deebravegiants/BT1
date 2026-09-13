# [C] CVE-2024-27561

## Summary
Severity: Critical
Advisory: CVE-2024-27561
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-05
Source: https://osv.dev/vulnerability/CVE-2024-27561
Type: osv

## Details
A Server-Side Request Forgery (SSRF) in the installUpdateThemePluginAction function of WonderCMS v3.1.3 allows attackers to force the application to make arbitrary requests via injection of crafted URLs into the installThemePlugin parameter.

## References
- https://github.com/zer0yu/CVE_Request/blob/master/WonderCMS/wondercms_installUpdateThemePluginAction_plugins.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27561.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27561
