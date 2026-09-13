# [H] CVE-2022-1353

## Summary
Severity: High
Advisory: CVE-2022-1353
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-04-29
Source: https://osv.dev/vulnerability/CVE-2022-1353
Type: osv

## Details
A vulnerability was found in the pfkey_register function in net/key/af_key.c in the Linux kernel. This flaw allows a local, unprivileged user to gain access to kernel memory, leading to a system crash or a leak of internal kernel information.

## References
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://security.netapp.com/advisory/ntap-20220629-0001/
- https://www.debian.org/security/2022/dsa-5127
- https://www.debian.org/security/2022/dsa-5173
- https://bugzilla.redhat.com/show_bug.cgi?id=2066819
- https://github.com/torvalds/linux/commit/9a564bccb78a76740ea9d75a259942df8143d02c
