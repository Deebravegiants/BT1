# [M] CVE-2021-42762

## Summary
Severity: Medium
Advisory: CVE-2021-42762
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2021-10-20
Source: https://osv.dev/vulnerability/CVE-2021-42762
Type: osv

## Details
BubblewrapLauncher.cpp in WebKitGTK and WPE WebKit before 2.34.1 allows a limited sandbox bypass that allows a sandboxed process to trick host processes into thinking the sandboxed process is not confined by the sandbox, by abusing VFS syscalls that manipulate its filesystem namespace. The impact is limited to host services that create UNIX sockets that WebKit mounts inside its sandbox, and the sandboxed process remains otherwise confined. NOTE: this is similar to CVE-2021-41133.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M5J2LZQTDX53DNSKSGU7TQYCO2HKSTY4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ON5SDVVPVPCAGFPW2GHYATZVZYLPW2L4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H6MGXCX7P5AHWOQ6IRT477UKT7IS4DAD/
- http://www.openwall.com/lists/oss-security/2021/10/26/9
- http://www.openwall.com/lists/oss-security/2021/10/27/1
- http://www.openwall.com/lists/oss-security/2021/10/27/4
- https://www.debian.org/security/2021/dsa-4995
- https://www.debian.org/security/2021/dsa-4996
- http://www.openwall.com/lists/oss-security/2021/10/27/2
- https://github.com/flatpak/flatpak/security/advisories/GHSA-67h7-w3jq-vh4q
- https://bugs.webkit.org/show_bug.cgi?id=231479
