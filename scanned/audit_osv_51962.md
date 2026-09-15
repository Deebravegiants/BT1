# [H] CVE-2021-46828

## Summary
Severity: High
Advisory: CVE-2021-46828
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-20
Source: https://osv.dev/vulnerability/CVE-2021-46828
Type: osv

## Details
In libtirpc before 1.3.3rc1, remote attackers could exhaust the file descriptors of a process that uses libtirpc because idle TCP connections are mishandled. This can, in turn, lead to an svc_run infinite loop without accepting new connections.

## References
- http://git.linux-nfs.org/?p=steved/libtirpc.git%3Ba=commit%3Bh=86529758570cef4c73fb9b9c4104fdc510f701ed
- https://lists.debian.org/debian-lts-announce/2022/08/msg00004.html
- https://security.gentoo.org/glsa/202210-33
- https://security.netapp.com/advisory/ntap-20221007-0004/
- https://www.debian.org/security/2022/dsa-5200
