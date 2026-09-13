# [C] ipv6: exthdrs: refresh nh pointer after ipv6_hop_jumbo()

## Summary
Severity: Critical
Advisory: CVE-2026-63924
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63924
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: exthdrs: refresh nh pointer after ipv6_hop_jumbo()

ipv6_hop_jumbo() calls pskb_trim_rcsum(), which can change skb pointers.
Let's recompute nh pointer to make sure any change won't mess things up.

## References
- https://git.kernel.org/stable/c/2b56bbd928c030894c270cd33d60286326919458
- https://git.kernel.org/stable/c/645b99b1a185c91a79bdac4c5de0f91b212d64f0
- https://git.kernel.org/stable/c/72af7beae774e46ed543f3f2f267bf0a141bfcdd
- https://git.kernel.org/stable/c/9e883eaa878f4337b5873c706efb5a192364ed18
- https://git.kernel.org/stable/c/b3ac54e5c905f86d22b502eacb5686a282c5659f
- https://git.kernel.org/stable/c/bddaa4dfc7f36e1ee343a0622f69288af2b9ace9
- https://git.kernel.org/stable/c/c512e1c819dfbf6ae95ee7a44b65b9ad98979157
- https://git.kernel.org/stable/c/d47548a36639095939f4747d4c43f2271366f565
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63924.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
