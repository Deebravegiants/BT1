# [M] CVE-2019-16994

## Summary
Severity: Medium
Advisory: CVE-2019-16994
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-30
Source: https://osv.dev/vulnerability/CVE-2019-16994
Type: osv

## Details
In the Linux kernel before 5.0, a memory leak exists in sit_init_net() in net/ipv6/sit.c when register_netdev() fails to register sitn->fb_tunnel_dev, which may cause denial of service, aka CID-07f12b26e21a.

## References
- https://security.netapp.com/advisory/ntap-20191031-0005/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=07f12b26e21ab359261bf75cfcb424fdc7daeb6d
- https://github.com/torvalds/linux/commit/07f12b26e21ab359261bf75cfcb424fdc7daeb6d
