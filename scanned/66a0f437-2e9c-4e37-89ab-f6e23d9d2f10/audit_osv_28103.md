# [M] CVE-2024-27563

## Summary
Severity: Medium
Advisory: CVE-2024-27563
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-03-05
Source: https://osv.dev/vulnerability/CVE-2024-27563
Type: osv

## Details
A Server-Side Request Forgery (SSRF) in the getFileFromRepo function of WonderCMS v3.1.3 allows attackers to force the application to make arbitrary requests via injection of crafted URLs into the pluginThemeUrl parameter.

## References
- https://github.com/zer0yu/CVE_Request/blob/master/WonderCMS/wondercms_pluginThemeUrl.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27563.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27563
