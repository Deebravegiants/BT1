# [H] HashBrown CMS - OS Command Injection in Media Upload Thumbnail Generation

## Summary
Severity: High
Advisory: CVE-2026-70374
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-70374
Type: osv

## Details
HashBrown CMS through 1.4.6 contains an OS Command Injection vulnerability (CWE-78) in the media upload thumbnail generation routine. Media.generateThumbnail in src/Server/Entity/Resource/Media.js builds a temporary file path as 'thumbnail' + Path.extname(filename) and passes it, unescaped, into a shell command executed via AppService.exec ('convert ' + tempFile + ...).

## References
- https://cve.turansec.uz/advisories/TRN-11FC0D88
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70374.json
- https://github.com/HashBrownCMS/hashbrown-cms
- https://nvd.nist.gov/vuln/detail/CVE-2026-70374
