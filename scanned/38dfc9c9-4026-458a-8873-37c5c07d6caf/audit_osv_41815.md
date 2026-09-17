# [C] ipv6: exthdrs: refresh nh after handling HAO option

## Summary
Severity: Critical
Advisory: CVE-2026-63922
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63922
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: exthdrs: refresh nh after handling HAO option

ip6_parse_tlv() caches skb_network_header(skb) in nh while walking
IPv6 TLVs.

ipv6_dest_hao() may call pskb_expand_head() for a cloned skb, which can
move the skb head and invalidate the cached network header pointer.
Refresh nh after ipv6_dest_hao() returns so any trailing padding or TLVs
are parsed from the current skb head.

This matches the existing pattern used in ip6_parse_tlv() after helpers
that can modify skb header storage.

## References
- https://git.kernel.org/stable/c/12d957979e4a800167842f1b42be6a606d227ebe
- https://git.kernel.org/stable/c/1a11eb7431e3d2882f5bd5939c5a9bbc65ccf4d1
- https://git.kernel.org/stable/c/751db1b802a067b7fff25880f4e9f9152a171538
- https://git.kernel.org/stable/c/9b6dcc0a39fd71752937f0b6b3973e1416085dcf
- https://git.kernel.org/stable/c/b3ac54e5c905f86d22b502eacb5686a282c5659f
- https://git.kernel.org/stable/c/f7b52afe3592eae66e160586b45a3f2242972c63
- https://git.kernel.org/stable/c/f8aabed3ff3e986920cf02a2a2785e08e586b234
- https://git.kernel.org/stable/c/ff375ed1cba81392346c5bfbf0bb7a13b2946f99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63922.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63922
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
