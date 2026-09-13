# [C] Vvveb < 1.0.8.2 Authenticated RCE via Code Editor

## Summary
Severity: Critical
Advisory: CVE-2026-41934
Aliases: GHSA-vfjj-gcvv-w248
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-41934
Type: osv

## Details
Vvveb before version 1.0.8.2 contains an authenticated remote code execution vulnerability in the admin code editor that allows low-privilege authenticated users to execute arbitrary code through insufficient file extension restrictions, with the uploaded payload then executable via subsequent unauthenticated HTTP requests. Attackers with editor, author, contributor, or site_admin roles can write a malicious .htaccess file to map arbitrary extensions to the PHP handler, then upload PHP code with that extension to achieve unauthenticated remote code execution when the file is accessed via HTTP.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41934.json
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.2
- https://github.com/givanz/Vvveb/security/advisories/GHSA-vfjj-gcvv-w248
- https://nvd.nist.gov/vuln/detail/CVE-2026-41934
- https://www.vulncheck.com/advisories/vvveb-authenticated-rce-via-code-editor
- https://github.com/givanz/Vvveb/commit/1196561276a3f49da5a714fef89ac9a6c6f9e33b
