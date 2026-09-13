# [C] CVE-2019-18805

## Summary
Severity: Critical
Advisory: CVE-2019-18805
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18805
Type: osv

## Details
An issue was discovered in net/ipv4/sysctl_net_ipv4.c in the Linux kernel before 5.0.11. There is a net/ipv4/tcp_input.c signed integer overflow in tcp_ack_update_rtt() when userspace writes a very large integer to /proc/sys/net/ipv4/tcp_min_rtt_wlen, leading to a denial of service or possibly unspecified other impact, aka CID-19fad20d15a6.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00039.html
- https://access.redhat.com/errata/RHSA-2020:0740
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.11
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=19fad20d15a6494f47f85d869f00b11343ee5c78
