# [M] CVE-2021-28964

## Summary
Severity: Medium
Advisory: CVE-2021-28964
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-22
Source: https://osv.dev/vulnerability/CVE-2021-28964
Type: osv

## Details
A race condition was discovered in get_old_root in fs/btrfs/ctree.c in the Linux kernel through 5.11.8. It allows attackers to cause a denial of service (BUG) because of a lack of locking on an extent buffer before a cloning operation, aka CID-dbcc7d57bffc.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T2S3I4SLRNRUQDOFYUS6IUAZMQNMPNLG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4VCKIOXCOZGXBEZMO5LGGV5MWCHO6FT3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PTRNPQTZ4GVS46SZ4OBXY5YDOGVPSTGQ/
- https://security.netapp.com/advisory/ntap-20210430-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=dbcc7d57bffc0c8cac9dac11bec548597d59a6a5
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
