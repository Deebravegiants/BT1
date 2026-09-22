# [H] CVE-2021-42008

## Summary
Severity: High
Advisory: CVE-2021-42008
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-05
Source: https://osv.dev/vulnerability/CVE-2021-42008
Type: osv

## Details
The decode_data function in drivers/net/hamradio/6pack.c in the Linux kernel before 5.13.13 has a slab out-of-bounds write. Input from a process that has the CAP_NET_ADMIN capability can lead to root access.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.13
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://security.netapp.com/advisory/ntap-20211104-0002/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=19d1532a187669ce86d5a2696eb7275310070793
- https://www.youtube.com/watch?v=d5f9xLK8Vhw
