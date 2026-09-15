# [C] netfilter: ip6t_eui64: reject invalid MAC header for all packets

## Summary
Severity: Critical
Advisory: CVE-2026-31685
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31685
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ip6t_eui64: reject invalid MAC header for all packets

`eui64_mt6()` derives a modified EUI-64 from the Ethernet source address
and compares it with the low 64 bits of the IPv6 source address.

The existing guard only rejects an invalid MAC header when
`par->fragoff != 0`. For packets with `par->fragoff == 0`, `eui64_mt6()`
can still reach `eth_hdr(skb)` even when the MAC header is not valid.

Fix this by removing the `par->fragoff != 0` condition so that packets
with an invalid MAC header are rejected before accessing `eth_hdr(skb)`.

## References
- https://git.kernel.org/stable/c/288138418bef956f8b295751a4536c60f0e89f4a
- https://git.kernel.org/stable/c/309ae3e9a51a69699ca94eac5fac5688fa562d55
- https://git.kernel.org/stable/c/4d75bc2cd093bf5803edf512c099bfb220fd6459
- https://git.kernel.org/stable/c/7d6a57411caf54df025860c9b1a82cd42d57a562
- https://git.kernel.org/stable/c/807d6ee15804df6f01a35c910f09612e858739a6
- https://git.kernel.org/stable/c/9eda5478746ef7dc0e4e537b5a5e4b0ca1027091
- https://git.kernel.org/stable/c/d5603591373441fecf9951833d6d873e09320f08
- https://git.kernel.org/stable/c/fdce0b3590f724540795b874b4c8850c90e6b0a8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31685.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31685
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
