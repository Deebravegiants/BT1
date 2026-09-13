# [H] CVE-2021-45010

## Summary
Severity: High
Advisory: CVE-2021-45010
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-15
Source: https://osv.dev/vulnerability/CVE-2021-45010
Type: osv

## Details
A path traversal vulnerability in the file upload functionality in tinyfilemanager.php in Tiny File Manager before 2.4.7 allows remote attackers (with valid user accounts) to upload malicious PHP files to the webroot, leading to code execution.

## References
- https://febin0x4e4a.wordpress.com/2022/01/23/tiny-file-manager-authenticated-rce/
- https://github.com/prasathmani/tinyfilemanager/commit/2046bbde72ed76af0cfdcae082de629bcc4b44c7
- https://github.com/prasathmani/tinyfilemanager/pull/636
- https://github.com/prasathmani/tinyfilemanager/pull/636/files/a93fc321a3c89fdb9bee860bf6df5d89083298d1
- http://packetstormsecurity.com/files/166330/Tiny-File-Manager-2.4.6-Shell-Upload.html
- https://github.com/febinrev/tinyfilemanager-2.4.3-exploit/raw/main/exploit.sh
- https://raw.githubusercontent.com/febinrev/tinyfilemanager-2.4.6-exploit/main/exploit.sh
- https://sploitus.com/exploit?id=1337DAY-ID-37364&utm_source=rss&utm_medium=rss
