# [H] CVE-2022-4379

## Summary
Severity: High
Advisory: CVE-2022-4379
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-10
Source: https://osv.dev/vulnerability/CVE-2022-4379
Type: osv

## Details
A use-after-free vulnerability was found in __nfs42_ssc_open() in fs/nfs/nfs4file.c in the Linux kernel. This flaw allows an attacker to conduct a remote denial

## References
- https://seclists.org/oss-sec/2022/q4/185
- https://security.netapp.com/advisory/ntap-20230223-0004/
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LECFVUHKIRBV5JJBE3KQCLGKNYJPBRCN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RAVD6JIILAVSRHZ4VXSV3RAAGUXKVXZA/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=75333d48f92256a0dec91dbf07835e804fc411c0
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=aeba12b26c79fc35e07e511f692a8907037d95da
