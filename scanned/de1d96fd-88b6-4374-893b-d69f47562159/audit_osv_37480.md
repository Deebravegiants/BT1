# [H] batman-adv: avoid OGM aggregation when skb tailroom is insufficient

## Summary
Severity: High
Advisory: CVE-2026-31683
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31683
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: avoid OGM aggregation when skb tailroom is insufficient

When OGM aggregation state is toggled at runtime, an existing forwarded
packet may have been allocated with only packet_len bytes, while a later
packet can still be selected for aggregation. Appending in this case can
hit skb_put overflow conditions.

Reject aggregation when the target skb tailroom cannot accommodate the new
packet. The caller then falls back to creating a new forward packet
instead of appending.

## References
- https://git.kernel.org/stable/c/0b10a8b355c3f71012ce89289ec2c2f5e3bfd6c1
- https://git.kernel.org/stable/c/0d4aef630be9d5f9c1227d07669c26c4383b5ad0
- https://git.kernel.org/stable/c/0e35db29fc5a97a8553f7c2d3a2ba730e46b1ee8
- https://git.kernel.org/stable/c/1ada20331f2df2a942d6b83ae1f04a304b642e2a
- https://git.kernel.org/stable/c/67176c96f325837b0bb3e9538ca2eba414f447d8
- https://git.kernel.org/stable/c/6755347c5f9bdd44dee80f692208b056fcd40a52
- https://git.kernel.org/stable/c/6e40ebb999c2c3d2fbb3cacb61f0384ee6e69075
- https://git.kernel.org/stable/c/eda89a1bae0602aec8314ced299bb243b9f9aeef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31683.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31683
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
