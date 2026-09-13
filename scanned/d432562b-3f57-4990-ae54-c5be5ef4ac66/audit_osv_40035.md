# [H] e107: Command Injection via shell expansion in ImageMagick resize destination path

## Summary
Severity: High
Advisory: CVE-2026-48997
Aliases: GHSA-3j33-c9v4-4p42
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-48997
Type: osv

## Details
e107 is a content management system (CMS). Versions  2.3.5 and earlier contain a command injection vulnerability in the ImageMagick resize destination path. In resize_image(), the source path is escaped with escapeshellarg(), but the destination path is inserted inside raw double quotes in the convert command; in the submit-news upload flow, that destination filename includes the first six characters of user-controlled news title input. Because the title filter removes literal spaces but not tab characters, and shell expansions such as $(...) and backticks can survive into the quoted destination argument, /bin/sh -c may evaluate attacker-controlled input. Exploitation is possible only when all of the following non-default settings are enabled: resize_method=ImageMagick, subnews_attach=1, upload_enabled=1, subnews_resize is numeric between 30 and 5000, and the attacker is a non-admin in classes permitted by both subnews_class and upload_class. This issue has been fixed in version 2.3.6.

## References
- https://github.com/e107inc/e107/releases/tag/v2.3.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48997.json
- https://github.com/e107inc/e107/security/advisories/GHSA-3j33-c9v4-4p42
- https://nvd.nist.gov/vuln/detail/CVE-2026-48997
