# [M] CVE-2019-20812

## Summary
Severity: Medium
Advisory: CVE-2019-20812
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2019-20812
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.4.7. The prb_calc_retire_blk_tmo() function in net/packet/af_packet.c can result in a denial of service (CPU consumption and soft lockup) in a certain failure case involving TPACKET_V3, aka CID-b43d1f9f7067.

## References
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00008.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.7
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b43d1f9f7067c6759b1051e8ecb84e82cef569fe
