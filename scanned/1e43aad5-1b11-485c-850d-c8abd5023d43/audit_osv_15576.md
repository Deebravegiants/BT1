# [C] CVE-2019-17455

## Summary
Severity: Critical
Advisory: CVE-2019-17455
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-10
Source: https://osv.dev/vulnerability/CVE-2019-17455
Type: osv

## Details
Libntlm through 1.5 relies on a fixed buffer size for tSmbNtlmAuthRequest, tSmbNtlmAuthChallenge, and tSmbNtlmAuthResponse read and write operations, as demonstrated by a stack-based buffer over-read in buildSmbNtlmAuthRequest in smbutil.c for a crafted NTLM request.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3BVFO3OVJPMSGIXBKNOCVOJZ3UTGZQF5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZ5YWYNOJ5HMCKAHWLTY4MXZQWJJCBI7/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00026.html
- https://people.canonical.com/~ubuntu-security/cve/2019/CVE-2019-17455.html
- https://security-tracker.debian.org/tracker/CVE-2019-17455
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=942145
- https://gitlab.com/jas/libntlm/issues/2
