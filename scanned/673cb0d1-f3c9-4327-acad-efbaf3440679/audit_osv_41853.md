# [C] tunnels: load network headers after skb_cow() in iptunnel_pmtud_build_icmp[v6]()

## Summary
Severity: Critical
Advisory: CVE-2026-63994
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63994
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

tunnels: load network headers after skb_cow() in iptunnel_pmtud_build_icmp[v6]()

Sashiko found that iptunnel_pmtud_build_icmp() and
iptunnel_pmtud_build_icmpv6() were caching ip_hdr() and ipv6_hdr()
before an skb_cow() call which can reallocate skb->head.

Fix this possible UAF by initializing the local variables
after the skb_cow() call.

Remove skb_reset_network_header() calls which were not needed.

## References
- https://git.kernel.org/stable/c/50750d86a2e5266aba0c295483b3397843198b11
- https://git.kernel.org/stable/c/6dff77899b9e9fe5d854abda3a98ad04e7229ef7
- https://git.kernel.org/stable/c/7254aef4d1a7e18e887af9010e2f2dc34806789b
- https://git.kernel.org/stable/c/76cd9398a0470257ab765bdf5f358a2af2e17934
- https://git.kernel.org/stable/c/95b6d772bfe788331d9742d73eaa12e113b2adc4
- https://git.kernel.org/stable/c/b4bc94353050b1fa7b702bd4c6600710dd926cff
- https://git.kernel.org/stable/c/bf8b3f34c37c162357138e7c0942723b8b94fed1
- https://git.kernel.org/stable/c/f3f204541f280a6ecb04503a0d6794d93990ca43
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63994.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63994
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
