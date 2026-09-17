# [H] CVE-2019-12276

## Summary
Severity: High
Advisory: CVE-2019-12276
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-05
Source: https://osv.dev/vulnerability/CVE-2019-12276
Type: osv

## Details
A Path Traversal vulnerability in Controllers/LetsEncryptController.cs in LetsEncryptController in GrandNode 4.40 allows remote, unauthenticated attackers to retrieve arbitrary files on the web server via specially crafted LetsEncrypt/Index?fileName= HTTP requests. A patch for this issue was made on 2019-05-30 in GrandNode 4.40.

## References
- http://packetstormsecurity.com/files/153373/GrandNode-4.40-Path-Traversal-File-Download.html
- https://github.com/grandnode/grandnode
- https://grandnode.com
