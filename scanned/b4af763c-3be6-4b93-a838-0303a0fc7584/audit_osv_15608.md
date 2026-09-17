# [H] CVE-2019-17575

## Summary
Severity: High
Advisory: CVE-2019-17575
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-14
Source: https://osv.dev/vulnerability/CVE-2019-17575
Type: osv

## Details
A file-rename filter bypass exists in admin/media/rename.php in WBCE CMS 1.4.0 and earlier. This can be exploited by an authenticated user with admin privileges to rename a media filename and extension. (For example: place PHP code in a .jpg file, and then change the file's base name to filename.ph and change the file's extension to p. Because of concatenation, the name is then treated as filename.php.) At the result, remote attackers can execute arbitrary PHP code.

## References
- https://github.com/kbgsft/vuln-wbce/wiki/Arbitrary-file-upload-vulnerbility-in-WBCE-CMS-1.4.0
