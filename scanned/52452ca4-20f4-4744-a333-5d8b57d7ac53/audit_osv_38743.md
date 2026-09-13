# [C] Vvveb < 1.0.8.3 Unrestricted File Upload RCE via Plugin Upload

## Summary
Severity: Critical
Advisory: CVE-2026-41937
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-41937
Type: osv

## Details
Vvveb before 1.0.8.3 contains an unrestricted file upload vulnerability in the plugin upload endpoint that allows super_admin users to execute arbitrary PHP code by uploading a malicious plugin ZIP file. Attackers can craft a ZIP containing a plugin.php with a valid Slug header and a public/index.php file with arbitrary PHP code, which executes as the web server user once accessed via subsequent unauthenticated HTTP requests to the plugin's public path.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41937.json
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41937
- https://www.vulncheck.com/advisories/vvveb-unrestricted-file-upload-rce-via-plugin-upload
- https://github.com/givanz/Vvveb/commit/04f0294350ec429e307cd31c2e777a4797c868d6
- https://github.com/givanz/Vvveb
