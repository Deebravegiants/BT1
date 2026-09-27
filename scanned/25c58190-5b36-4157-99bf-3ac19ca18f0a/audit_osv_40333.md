# [H] neigh: let neigh_xmit take skb ownership

## Summary
Severity: High
Advisory: CVE-2026-52981
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52981
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

neigh: let neigh_xmit take skb ownership

neigh_xmit always releases the skb, except when no neighbour table is
found. But even the first added user of neigh_xmit (mpls) relied on
neigh_xmit to release the skb (or queue it for tx).

sashiko reported:
 If neigh_xmit() is called with an uninitialized neighbor table (for
 example, NEIGH_ND_TABLE when IPv6 is disabled), it returns -EAFNOSUPPORT
 and bypasses its internal out_kfree_skb error path.  Because the return
 value of neigh_xmit() is ignored here, does this leak the SKB?

Assume full ownership and remove the last code path that doesn't
xmit or free skb.

## References
- https://git.kernel.org/stable/c/0084712e0bee204b284510cdb63182fd5a30c2b7
- https://git.kernel.org/stable/c/4438113be604ee67a7bf4f81da6e1cca41332ce4
- https://git.kernel.org/stable/c/445e45a2c3a078316a62d2d331a570cf34ef5079
- https://git.kernel.org/stable/c/63063ba60d2dc334e34f1e3f9271d7f3f6f30307
- https://git.kernel.org/stable/c/8a89054a1ec0767aec25ed2bbac933da6ba3cf5a
- https://git.kernel.org/stable/c/9247d59ca15bf60a57dca08103f055d8a4340877
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52981.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52981
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
