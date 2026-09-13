# [M] CVE-2022-3643

## Summary
Severity: Medium
Advisory: CVE-2022-3643
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-12-07
Source: https://osv.dev/vulnerability/CVE-2022-3643
Type: osv

## Details
Guests can trigger NIC interface reset/abort/crash via netback It is possible for a guest to trigger a NIC interface reset/abort/crash in a Linux based network backend by sending certain kinds of packets. It appears to be an (unwritten?) assumption in the rest of the Linux network stack that packet protocol headers are all contained within the linear section of the SKB and some NICs behave badly if this is not the case. This has been reported to occur with Cisco (enic) and Broadcom NetXtrem II BCM5780 (bnx2x) though it may be an issue with other NICs/drivers as well. In case the frontend is sending requests with split headers, netback will forward those violating above mentioned assumption to the networking core, resulting in said misbehavior.

## References
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- https://xenbits.xenproject.org/xsa/advisory-423.txt
- http://www.openwall.com/lists/oss-security/2022/12/07/2
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
