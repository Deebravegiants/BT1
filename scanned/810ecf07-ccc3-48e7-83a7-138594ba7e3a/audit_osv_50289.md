# [M] CVE-2020-10942

## Summary
Severity: Medium
Advisory: CVE-2020-10942
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2020-03-24
Source: https://osv.dev/vulnerability/CVE-2020-10942
Type: osv

## Details
In the Linux kernel before 5.5.8, get_raw_socket in drivers/vhost/net.c lacks validation of an sk_family field, which might allow attackers to trigger kernel stack corruption via crafted system calls.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00035.html
- https://usn.ubuntu.com/4364-1/
- http://www.openwall.com/lists/oss-security/2020/04/15/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.8
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://usn.ubuntu.com/4342-1/
- https://usn.ubuntu.com/4344-1/
- https://security.netapp.com/advisory/ntap-20200403-0003/
- https://usn.ubuntu.com/4345-1/
- https://www.debian.org/security/2020/dsa-4667
- https://www.debian.org/security/2020/dsa-4698
- https://git.kernel.org/linus/42d84c8490f9f0931786f1623191fcab397c3d64
- https://lkml.org/lkml/2020/2/15/125
