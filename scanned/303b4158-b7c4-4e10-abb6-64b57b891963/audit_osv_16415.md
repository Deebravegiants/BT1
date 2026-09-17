# [C] CVE-2019-6714

## Summary
Severity: Critical
Advisory: CVE-2019-6714
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-6714
Type: osv

## Details
An issue was discovered in BlogEngine.NET through 3.3.6.0. A path traversal and Local File Inclusion vulnerability in PostList.ascx.cs can cause unauthenticated users to load a PostView.ascx component from a potentially untrusted location on the local filesystem. This is especially dangerous if an authenticated user uploads a PostView.ascx file using the file manager utility, which is currently allowed. This results in remote code execution for an authenticated user.

## References
- http://seclists.org/fulldisclosure/2019/Jun/26
- https://github.com/rxtur/BlogEngine.NET/
- https://blogengine.io/
- http://packetstormsecurity.com/files/151628/BlogEngine.NET-3.3.6-Directory-Traversal-Remote-Code-Execution.html
- https://www.exploit-db.com/exploits/46353/
