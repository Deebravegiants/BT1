# [C] CVE-2020-15692

## Summary
Severity: Critical
Advisory: CVE-2020-15692
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-14
Source: https://osv.dev/vulnerability/CVE-2020-15692
Type: osv

## Details
In Nim 1.2.4, the standard library browsers mishandles the URL argument to browsers.openDefaultBrowser. This argument can be a local file path that will be opened in the default explorer. An attacker can pass one argument to the underlying open command to execute arbitrary registered system commands.

## References
- https://nim-lang.org/blog/2020/07/30/versions-126-and-108-released.html
- https://github.com/nim-lang/Nim/blob/dc5a40f3f39c6ea672e6dc6aca7f8118a69dda99/lib/pure/browsers.nim#L48
- http://www.openwall.com/lists/oss-security/2021/02/04/1
- https://consensys.net/diligence/vulnerabilities/nim-browsers-argument-injection/
