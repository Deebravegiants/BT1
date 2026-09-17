# [C] openvswitch: fix GSO userspace truncation underflow

## Summary
Severity: Critical
Advisory: CVE-2026-68123
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68123
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

openvswitch: fix GSO userspace truncation underflow

OVS_ACTION_ATTR_TRUNC currently stores a delta from the original skb
length in OVS_CB(skb)->cutlen. When a later userspace action segments a
GSO skb, queue_gso_packets() reuses that delta for each smaller segment.
A segment can then reach queue_userspace_packet() with cutlen greater
than skb->len, underflowing the length passed to skb_zerocopy().

Store the maximum preserved length instead and bound each consumer
against the current skb length. Use U32_MAX as the no-truncation
sentinel so the value remains valid if skb geometry changes before a
consumer handles it.

## References
- https://git.kernel.org/stable/c/100a23b1613e9218e0af654ef102352c713f0263
- https://git.kernel.org/stable/c/2623c48cc3a8da9a1886fd8f65c0e348f4406fd6
- https://git.kernel.org/stable/c/4032f8ed10fcb84d41c508dfb04be96589f78dfe
- https://git.kernel.org/stable/c/50a6a85f3d6b1d22d8436848606cdef5d2c490b4
- https://git.kernel.org/stable/c/a16eaaf7c0b0ccdef6166707d90ffbc6eebf6855
- https://git.kernel.org/stable/c/e211b081901ffca76674082c73eeaed53524c369
- https://git.kernel.org/stable/c/ea85dbcbe8d4056ecb54352f97743d138ea4c407
- https://git.kernel.org/stable/c/fbfa3ad2ad6f3a5624aba5211c46290fb98cc9dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68123.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68123
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
