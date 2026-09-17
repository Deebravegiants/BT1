# [H] CVE-2020-8835

## Summary
Severity: High
Advisory: CVE-2020-8835
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-02
Source: https://osv.dev/vulnerability/CVE-2020-8835
Type: osv

## Details
In the Linux kernel 5.5.0 and newer, the bpf verifier (kernel/bpf/verifier.c) did not properly restrict the register bounds for 32-bit operations, leading to out-of-bounds reads and writes in kernel memory. The vulnerability also affects the Linux 5.4 stable series, starting with v5.4.7, as the introducing commit was backported to that branch. This vulnerability was fixed in 5.6.1, 5.5.14, and 5.4.29. (issue is aka ZDI-CAN-10780)

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TF4PQZBEPNXDSK5DOBMW54OCLP25FTCD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F7OONYGMSYBEFHLHZJK3GOI5Z553G4LD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YXBWSHZ6DJIZVXKXGZPK6QPFCY7VKZEG/
- https://lore.kernel.org/bpf/20200330160324.15259-1-daniel%40iogearbox.net/T/
- https://security.netapp.com/advisory/ntap-20200430-0004/
- https://usn.ubuntu.com/usn/usn-4313-1
- https://usn.ubuntu.com/4313-1/
- https://www.thezdi.com/blog/2020/3/19/pwn2own-2020-day-one-results
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f2d67fec0b43edce8c416101cdc52e71145b5fef
- https://www.openwall.com/lists/oss-security/2020/03/30/3
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net-next.git/commit/?id=f2d67fec0b43edce8c416101cdc52e71145b5fef
- http://www.openwall.com/lists/oss-security/2021/07/20/1
