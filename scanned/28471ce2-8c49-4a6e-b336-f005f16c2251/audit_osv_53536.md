# [M] CVE-2022-47946

## Summary
Severity: Medium
Advisory: CVE-2022-47946
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-23
Source: https://osv.dev/vulnerability/CVE-2022-47946
Type: osv

## Details
An issue was discovered in the Linux kernel 5.10.x before 5.10.155. A use-after-free in io_sqpoll_wait_sq in fs/io_uring.c allows an attacker to crash the kernel, resulting in denial of service. finish_wait can be skipped. An attack can occur in some situations by forking a process and then quickly terminating it. NOTE: later kernel versions, such as the 5.15 longterm series, substantially changed the implementation of io_sqpoll_wait_sq.

## References
- http://www.openwall.com/lists/oss-security/2022/12/27/1
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?h=v5.10.161&id=0f544353fec8e717d37724d95b92538e1de79e86
- https://www.openwall.com/lists/oss-security/2022/12/22/2
