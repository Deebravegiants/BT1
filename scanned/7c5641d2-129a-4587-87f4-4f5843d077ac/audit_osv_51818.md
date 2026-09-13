# [H] CVE-2021-41073

## Summary
Severity: High
Advisory: CVE-2021-41073
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-19
Source: https://osv.dev/vulnerability/CVE-2021-41073
Type: osv

## Details
loop_rw_iter in fs/io_uring.c in the Linux kernel 5.10 through 5.14.6 allows local users to gain privileges by using IORING_OP_PROVIDE_BUFFERS to trigger a free of a kernel buffer, as demonstrated by using /proc/<pid>/maps for exploitation.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J7KSMIOQ4377CVTHMWNGNCWHMCRFRP2T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PAP4TXEZ7J4EZQMQW5SIJMWXG7WZT3F7/
- https://www.debian.org/security/2021/dsa-4978
- http://www.openwall.com/lists/oss-security/2021/09/18/2
- http://www.openwall.com/lists/oss-security/2022/06/04/4
- https://security.netapp.com/advisory/ntap-20211014-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=16c8d2df7ec0eed31b7d3b61cb13206a7fb930cc
