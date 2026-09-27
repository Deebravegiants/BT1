# [H] batman-adv: retrieve ethhdr after potential skb realloc on RX

## Summary
Severity: High
Advisory: CVE-2026-72235
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72235
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: retrieve ethhdr after potential skb realloc on RX

pskb_may_pull() in batadv_interface_rx() could reallocate the buffer behind
the skb. Variables which were pointing to the old buffer need to be
reassigned to avoid an use-after-free.

This was done correctly for the VLAN header but missed for the ethernet
header which is later used for the TT and AP isolation handling.

## References
- https://git.kernel.org/stable/c/035e1fed892d3d06002a73ff73668f618a514644
- https://git.kernel.org/stable/c/2cefa5141cab8ec1e4b24cf585958b13f2e3049d
- https://git.kernel.org/stable/c/6abf73589bed3f27ee240c08108feb72bed0b9c6
- https://git.kernel.org/stable/c/6e189f14d1ea28db212b9d70a02131a7ce518012
- https://git.kernel.org/stable/c/85a71a81854e0e191ad0e533eabb4eff54866feb
- https://git.kernel.org/stable/c/a1820344b180cb55af748f102bc536b5c93164db
- https://git.kernel.org/stable/c/b031fc97e1993d29d6c3a0e86a99140528cf31e8
- https://git.kernel.org/stable/c/f19259395b44af67f3c274e34237c295b526b859
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72235.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72235
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
