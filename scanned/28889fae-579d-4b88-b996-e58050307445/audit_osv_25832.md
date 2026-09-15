# [H] SQL injection vulnerability in Farmbot-Web-App

## Summary
Severity: High
Advisory: CVE-2023-45674
Aliases: GHSA-pgq5-ff74-g7xq
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-10-13
Source: https://osv.dev/vulnerability/CVE-2023-45674
Type: osv

## Details
Farmbot-Web-App is a web control interface for the Farmbot farm automation platform. An SQL injection vulnerability was found in FarmBot's web app that allows authenticated attackers to extract arbitrary data from its database (including the user table). This issue may lead to Information Disclosure. This issue has been patched in version 15.8.4. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45674.json
- https://github.com/FarmBot/Farmbot-Web-App/security/advisories/GHSA-pgq5-ff74-g7xq
- https://nvd.nist.gov/vuln/detail/CVE-2023-45674
