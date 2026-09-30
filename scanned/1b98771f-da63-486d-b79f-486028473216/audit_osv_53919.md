# [M] CVE-2023-32269

## Summary
Severity: Medium
Advisory: CVE-2023-32269
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-05
Source: https://osv.dev/vulnerability/CVE-2023-32269
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.1.11. In net/netrom/af_netrom.c, there is a use-after-free because accept is also allowed for a successfully connected AF_NETROM socket. However, in order for an attacker to exploit this, the system must have netrom routing configured or the attacker must have the CAP_NET_ADMIN capability.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.11
- https://github.com/torvalds/linux/commit/611792920925fb088ddccbe2783c7f92fdfb6b64
