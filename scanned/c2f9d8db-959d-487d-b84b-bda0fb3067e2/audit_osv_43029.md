# [C] netfilter: ip6tables: mark malformed IPv6 extension headers for hotdrop

## Summary
Severity: Critical
Advisory: CVE-2026-72348
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72348
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ip6tables: mark malformed IPv6 extension headers for hotdrop

The ah, hbh and rt matches check that the fixed extension header is
present, then use the header length field to derive the advertised
extension header length for matching.

For the ah match, add the missing advertised-length check. For hbh
and rt, update the existing advertised-length checks. In all three
cases, set hotdrop to true before returning false when the advertised
extension header length exceeds the available skb data.

Returning false treats the packet as a rule mismatch. Set hotdrop to
true and drop malformed packets so they cannot bypass rules intended
to drop packets with these IPv6 extension headers.

## References
- https://git.kernel.org/stable/c/2fd89a50a9783eed8ed23866b11c8b3d8779a7a8
- https://git.kernel.org/stable/c/3578b6d92a5b1e603ae6e8c8f5538a709f03aba4
- https://git.kernel.org/stable/c/3d441be2b1c5e98167302fa1c7b61960a067b112
- https://git.kernel.org/stable/c/43ccc20b5a733226417832cf16ef45322e594990
- https://git.kernel.org/stable/c/d5e39e5eb6b30bc4a3bb7aba54c293cf36a806c7
- https://git.kernel.org/stable/c/f16d856b6af5fd0e7cb0b0212f70825b599ef72e
- https://git.kernel.org/stable/c/f775fcf384b06f35b612f78fa5601fee99eb6513
- https://git.kernel.org/stable/c/fc416870100cf16d5b9495199355a679c3a02d48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72348.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72348
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
