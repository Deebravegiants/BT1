# [C] CVE-2019-3464

## Summary
Severity: Critical
Advisory: CVE-2019-3464
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-06
Source: https://osv.dev/vulnerability/CVE-2019-3464
Type: osv

## Details
Insufficient sanitization of environment variables passed to rsync can bypass the restrictions imposed by rssh, a restricted shell that should restrict users to perform only rsync operations, resulting in the execution of arbitrary shell commands.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KR2OHTHMJVV4DO3HDRFQQZ5JENHDJQEN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HO3MDU3AH5SLYBKHH5PJ6PHC63ASIF42/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T42YYNWJZG422GATWAHAEK4A24OKY557/
- https://usn.ubuntu.com/3946-1/
- https://www.debian.org/security/2019/dsa-4382
- http://seclists.org/fulldisclosure/2021/May/78
- https://tracker.debian.org/news/1026713/accepted-rssh-234-5deb9u2-source-amd64-into-stable-embargoed-stable/
- http://www.securityfocus.com/bid/106839
- https://lists.debian.org/debian-lts-announce/2019/02/msg00007.html
- https://security.gentoo.org/glsa/202007-29
