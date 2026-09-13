# [M] CVE-2021-28951

## Summary
Severity: Medium
Advisory: CVE-2021-28951
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-20
Source: https://osv.dev/vulnerability/CVE-2021-28951
Type: osv

## Details
An issue was discovered in fs/io_uring.c in the Linux kernel through 5.11.8. It allows attackers to cause a denial of service (deadlock) because exit may be waiting to park a SQPOLL thread, but concurrently that SQPOLL thread is waiting for a signal to start, aka CID-3ebba796fa25.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4VCKIOXCOZGXBEZMO5LGGV5MWCHO6FT3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PTRNPQTZ4GVS46SZ4OBXY5YDOGVPSTGQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T2S3I4SLRNRUQDOFYUS6IUAZMQNMPNLG/
- https://security.netapp.com/advisory/ntap-20210430-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=3ebba796fa251d042be42b929a2d916ee5c34a49
