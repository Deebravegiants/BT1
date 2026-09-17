# [H] ipvs: avoid out-of-bounds write in ip_vs_nat_icmp

## Summary
Severity: High
Advisory: CVE-2026-74724
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74724
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: avoid out-of-bounds write in ip_vs_nat_icmp

Sashiko warns that local attacker can modify the packet
while it is processed by IPVS. Some places read the
IP ihl field multiple times which can cause out-of-bounds
access. One such place is ip_vs_nat_icmp where we
can write after the validated area.

Fix it by providing ciph argument just like it is done for
IPv6 and use ciph->len as offset to the embedded transport
header.

Modify some IPv4 header checks by reading the ihl field
only once.

## References
- https://git.kernel.org/stable/c/243d0187ec4c3837b9b0004f18d1068e46115760
- https://git.kernel.org/stable/c/3b8f79af0e98f27b932b0b416e9c52b692d31ff9
- https://git.kernel.org/stable/c/3c779b258c9c3c3567af68d4f45c2f751f35bd0e
- https://git.kernel.org/stable/c/646922a0379496154e8c8faca4f8e2fd9100cacc
- https://git.kernel.org/stable/c/a69a4b3fff5814d079beff9a1e9d369994b2ed47
- https://git.kernel.org/stable/c/be65fa324640c7a95e30b146159a2be5cc73f22e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74724.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74724
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
