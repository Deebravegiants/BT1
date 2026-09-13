# [C] Vvveb < 1.0.8.2 RCE via Media Upload Handler

## Summary
Severity: Critical
Advisory: CVE-2026-41938
Aliases: CVE-2026-41929, GHSA-wwmv-4g9g-p48g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-41938
Type: osv

## Details
Vvveb before version 1.0.8.2 contains an unrestricted file upload vulnerability in the media upload handler that allows authenticated users with media-upload permissions to bypass extension restrictions by uploading a .htaccess file to map .phtml extensions to the PHP handler. Attackers can upload a .phtml file containing arbitrary PHP code and execute the uploaded payload through a subsequent unauthenticated HTTP GET request to the uploaded file, resulting in remote code execution with web server privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41938.json
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.2
- https://github.com/givanz/Vvveb/security/advisories/GHSA-wwmv-4g9g-p48g
- https://nvd.nist.gov/vuln/detail/CVE-2026-41938
- https://www.vulncheck.com/advisories/vvveb-rce-via-media-upload-handler
- https://github.com/givanz/Vvveb/commit/54a9e846fb94192f1b31ae81d81d25c874662e6a
