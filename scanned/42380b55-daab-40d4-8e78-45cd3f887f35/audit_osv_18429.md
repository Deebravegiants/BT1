# [M] CVE-2020-27617

## Summary
Severity: Medium
Advisory: CVE-2020-27617
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/CVE-2020-27617
Type: osv

## Details
eth_get_gso_type in net/eth.c in QEMU 4.2.1 allows guest OS users to trigger an assertion failure. A guest can crash the QEMU process via packet data that lacks a valid Layer 3 protocol.

## References
- https://lists.debian.org/debian-lts-announce/2020/11/msg00047.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.netapp.com/advisory/ntap-20201202-0002/
- http://www.openwall.com/lists/oss-security/2020/11/02/1
- https://lists.nongnu.org/archive/html/qemu-devel/2020-10/msg05731.html
