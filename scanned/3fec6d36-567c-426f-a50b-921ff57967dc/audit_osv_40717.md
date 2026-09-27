# [M] InstantCMS has Remote Code Execution in package installer

## Summary
Severity: Medium
Advisory: CVE-2026-54611
Aliases: GHSA-vvgv-h28h-p2m5
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-54611
Type: osv

## Details
InstantCMS is a free and open source content management system. Versions prior to 2.18.2 have a Remote Code Execution (RCE) issue that allows remote authenticated attackers to execute any PHP code via the component installer. It is possible to upload a malicious component into the server, however, it won't be installed, but upload files will be executed. Normally all php files in upload folder are not executed, however, by uploading custom .htaccess it becomes possible. Version 2.18.2 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54611.json
- https://github.com/instantsoft/icms2/security/advisories/GHSA-vvgv-h28h-p2m5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54611
- https://github.com/instantsoft/icms2/commit/44f3a9d04a3207c82cdc756599cbdf084a02858f
