# [H] netfilter: ctnetlink: ensure safe access to master conntrack

## Summary
Severity: High
Advisory: CVE-2026-43116
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43116
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ctnetlink: ensure safe access to master conntrack

Holding reference on the expectation is not sufficient, the master
conntrack object can just go away, making exp->master invalid.

To access exp->master safely:

- Grab the nf_conntrack_expect_lock, this gets serialized with
  clean_from_lists() which also holds this lock when the master
  conntrack goes away.

- Hold reference on master conntrack via nf_conntrack_find_get().
  Not so easy since the master tuple to look up for the master conntrack
  is not available in the existing problematic paths.

This patch goes for extending the nf_conntrack_expect_lock section
to address this issue for simplicity, in the cases that are described
below this is just slightly extending the lock section.

The add expectation command already holds a reference to the master
conntrack from ctnetlink_create_expect().

However, the delete expectation command needs to grab the spinlock
before looking up for the expectation. Expand the existing spinlock
section to address this to cover the expectation lookup. Note that,
the nf_ct_expect_iterate_net() calls already grabs the spinlock while
iterating over the expectation table, which is correct.

The get expectation command needs to grab the spinlock to ensure master
conntrack does not go away. This also expands the existing spinlock
section to cover the expectation lookup too. I needed to move the
netlink skb allocation out of the spinlock to keep it GFP_KERNEL.

For the expectation events, the IPEXP_DESTROY event is already delivered
under the spinlock, just move the delivery of IPEXP_NEW under the
spinlock too because the master conntrack event cache is reached through
exp->master.

While at it, add lockdep notations to help identify what codepaths need
to grab the spinlock.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/497f99b26fffdc5635706d1b4811f1ed8ee21a5b
- https://git.kernel.org/stable/c/5e1c1d22268ae710c238342c8030c21daf298168
- https://git.kernel.org/stable/c/9e1196d27ef496f404c76f7a9d03761142d991c4
- https://git.kernel.org/stable/c/bffcaad9afdfe45d7fc777397d3b83c1e3ebffe5
- https://git.kernel.org/stable/c/d52fa1fa7440676b8c238037a050ab008c22737f
- https://git.kernel.org/stable/c/f338ced0473849c9f6ed0b77ca99f1aab5826787
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43116.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43116
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
