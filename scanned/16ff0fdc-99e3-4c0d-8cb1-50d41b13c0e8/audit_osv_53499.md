# [H] CVE-2022-45934

## Summary
Severity: High
Advisory: CVE-2022-45934
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-27
Source: https://osv.dev/vulnerability/CVE-2022-45934
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.0.10. l2cap_config_req in net/bluetooth/l2cap_core.c has an integer wraparound via L2CAP_CONF_REQ packets.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NDAKCGDW6CQ6G3RZWYZJO454R3L5CTQB/
- https://lists.debian.org/debian-lts-announce/2023/03/msg00000.html
- https://security.netapp.com/advisory/ntap-20230113-0008/
- https://www.debian.org/security/2023/dsa-5324
- https://git.kernel.org/pub/scm/linux/kernel/git/bluetooth/bluetooth-next.git/commit/?id=ae4569813a6e931258db627cdfe50dfb4f917d5d
