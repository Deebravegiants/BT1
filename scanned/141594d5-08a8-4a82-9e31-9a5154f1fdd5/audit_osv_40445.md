# [C] ip6_vti: fix incorrect tunnel matching in vti6_tnl_lookup()

## Summary
Severity: Critical
Advisory: CVE-2026-53221
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53221
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip6_vti: fix incorrect tunnel matching in vti6_tnl_lookup()

In vti6_tnl_lookup(), when an exact match for a tunnel fails,
the code falls back to searching for wildcard tunnels:

- Tunnels matching the packet's local address, with any remote address
  wildcard remote).

- Tunnels matching the packet's remote address, with any local address
  (wildcard local).

However, vti6 stores all these different types of tunnels in the same
hash table (ip6n->tnls_r_l) prone to hash collisions.

The bug is that the fallback search loops in vti6_tnl_lookup() were
missing checks to ensure that the candidate tunnel actually has
a wildcard address.

## References
- https://git.kernel.org/stable/c/2abfb19bbb81958714ad1d43ebeb65b30394184b
- https://git.kernel.org/stable/c/2fc7bc087cc7085368263d9d37bfe9a0bddd6a2d
- https://git.kernel.org/stable/c/47fb3c2b4203556308e64354b3e78f2ce221d646
- https://git.kernel.org/stable/c/90fd4513315ca07da99cfd8549d3e553a7160f0d
- https://git.kernel.org/stable/c/a5c0359f5cbc51a2e2b114d6041e0f3c73f903e9
- https://git.kernel.org/stable/c/c327fa4fca31415431202e063767a7ae342e19c6
- https://git.kernel.org/stable/c/f513f308cc4bdb4530d033431592ffbc29b7fca1
- https://git.kernel.org/stable/c/fc657ac0767c49839b3ef0b08dc0953ca30883f8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53221.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53221
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
