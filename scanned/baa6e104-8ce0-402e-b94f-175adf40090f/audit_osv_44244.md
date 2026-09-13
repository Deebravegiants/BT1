# [H] netfilter: xt_nat: reject unsupported target families

## Summary
Severity: High
Advisory: CVE-2026-80664
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80664
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: xt_nat: reject unsupported target families

xt_nat SNAT and DNAT target handlers assume IP-family conntrack state
is present and can dereference a NULL pointer when instantiated from an
unsupported family through nft_compat. A bridge-family compat rule can
therefore trigger a NULL-dereference in nf_nat_setup_info().

Reject non-IP families in xt_nat_checkentry() so unsupported targets
cannot be installed. Keep NFPROTO_INET allowed for valid inet NAT
compat users and leave the runtime fast path unchanged.

[ The crash was fixed via
  9dbba7e694ec ("netfilter: nft_compat: ebtables emulation must reject non-bridge targets"),
  so this patch is no longer critical.
  Nevertheless, NAT is only relevant for ipv4/ipv6, so this extra
  family check is a good idea in any case. ]

## References
- https://git.kernel.org/stable/c/0afc9ad987c0faa80ab5f8d6e7815085ac8dbb82
- https://git.kernel.org/stable/c/49abe564391411057a26a9a943c8e17867c3b9b4
- https://git.kernel.org/stable/c/4fbc2bac02edabb665beb2aa87ca6f1e1d4c4777
- https://git.kernel.org/stable/c/5d1a2240935ea47e2673d0ea17fdb058e4dc91dd
- https://git.kernel.org/stable/c/679ced28a9dc2f6dc679eb05027d779693e60902
- https://git.kernel.org/stable/c/a842dab87cab29f2a5798a47b2dc5e6a449950bf
- https://git.kernel.org/stable/c/e35c048d7511e9d4c2a537b8a231c49606e97c16
- https://git.kernel.org/stable/c/ec88fa71c82072e9189983b05b499d3507550271
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80664.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80664
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
