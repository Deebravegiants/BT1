# [C] xfrm: fix stale skb->prev after async crypto steals a GSO segment

## Summary
Severity: Critical
Advisory: CVE-2026-68426
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68426
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: fix stale skb->prev after async crypto steals a GSO segment

skb_gso_segment() leaves the segment list head with ->prev pointing at
the last segment, an invariant validate_xmit_skb_list() relies on when
it sets its tail pointer (tail = skb->prev).

When validate_xmit_xfrm() walks a GSO list and some segments are stolen
by async crypto (->xmit() returns -EINPROGRESS), those segments are
unlinked from the list but the head ->prev is never updated.  If the
last segment is the one stolen, the returned head still has ->prev
pointing at it, even though it is now owned by the crypto engine and may
be freed.  validate_xmit_skb_list() later does tail->next = skb, writing
through that stale pointer -- a use-after-free.

Repoint skb->prev at the last retained segment before returning.

## References
- https://git.kernel.org/stable/c/33e1b0d25ca0d2818c635ff80e6aa0d295e08a98
- https://git.kernel.org/stable/c/3f4c3919baf0944ad96580467c302bc6c7758b00
- https://git.kernel.org/stable/c/bbca7cc3b2b4b10afbfee99b81d9ee78f5423046
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68426.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68426
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
