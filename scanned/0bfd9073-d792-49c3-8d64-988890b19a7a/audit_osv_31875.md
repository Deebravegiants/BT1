# [H] vlan: enforce underlying device type

## Summary
Severity: High
Advisory: CVE-2025-21920
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21920
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

vlan: enforce underlying device type

Currently, VLAN devices can be created on top of non-ethernet devices.

Besides the fact that it doesn't make much sense, this also causes a
bug which leaks the address of a kernel function to usermode.

When creating a VLAN device, we initialize GARP (garp_init_applicant)
and MRP (mrp_init_applicant) for the underlying device.

As part of the initialization process, we add the multicast address of
each applicant to the underlying device, by calling dev_mc_add.

__dev_mc_add uses dev->addr_len to determine the length of the new
multicast address.

This causes an out-of-bounds read if dev->addr_len is greater than 6,
since the multicast addresses provided by GARP and MRP are only 6
bytes long.

This behaviour can be reproduced using the following commands:

ip tunnel add gretest mode ip6gre local ::1 remote ::2 dev lo
ip l set up dev gretest
ip link add link gretest name vlantest type vlan id 100

Then, the following command will display the address of garp_pdu_rcv:

ip maddr show | grep 01:80:c2:00:00:21

Fix the bug by enforcing the type of the underlying device during VLAN
device initialization.

## References
- https://git.kernel.org/stable/c/0fb7aa04c19eac4417f360a9f7611a60637bdacc
- https://git.kernel.org/stable/c/30e8aee77899173a82ae5ed89f536c096f20aaeb
- https://git.kernel.org/stable/c/3561442599804905c3defca241787cd4546e99a7
- https://git.kernel.org/stable/c/5a515d13e15536e82c5c7c83eb6cf5bc4827fee5
- https://git.kernel.org/stable/c/7f1564b2b2072b7aa1ac75350e9560a07c7a44fd
- https://git.kernel.org/stable/c/b33a534610067ade2bdaf2052900aaad99701353
- https://git.kernel.org/stable/c/b6c72479748b7ea09f53ed64b223cee6463dc278
- https://git.kernel.org/stable/c/fa40ebef69234e39ec2d26930d045f2fb9a8cb2b
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21920.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21920
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
