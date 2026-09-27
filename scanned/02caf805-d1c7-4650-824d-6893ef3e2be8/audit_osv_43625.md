# [H] netfilter: ipset: do not update comments from kernel-side hash adds

## Summary
Severity: High
Advisory: CVE-2026-74492
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74492
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: do not update comments from kernel-side hash adds

mtype_resize() copies comment pointers with memcpy(), not the comment
objects themselves. During the window after an entry has been copied but
before the table swap and backlog replay, the old table is still
published for packet-side updates while the replacement-table entry
already holds the same ip_set_comment_rcu pointer.

If xt_SET --add-set ... --exist hits that old entry in this window,
mtype_add() calls ip_set_init_comment() even though packet-side adds
carry no comment payload. That call frees the shared comment through the
old entry, so the replacement-table entry now holds a stale pointer.
When the queued add is replayed on the new table, mtype_add() calls
ip_set_init_comment() again and strlen() dereferences the stale pointer.

Fix this in mtype_add() by skipping ip_set_init_comment() when
ext->target marks a packet-side add. Userspace adds still update
comments, while packet-side adds can no longer free comment storage
shared with a resize copy.

## References
- https://git.kernel.org/stable/c/16bfa7be2d76ca1e0aacfa363482e1bf8ab5042a
- https://git.kernel.org/stable/c/4ae701848e4ba9e9713375fb7d82218cbd309da2
- https://git.kernel.org/stable/c/661ff9c0cfbe07f8eed920dde9f7781491738207
- https://git.kernel.org/stable/c/6f13f4d52d06986c18f12e8bffaab944dd27ceab
- https://git.kernel.org/stable/c/77dbb248a5cc7a5270cd37bbb0b635bf059a872a
- https://git.kernel.org/stable/c/c710e9bf38e4e71a8db85d26a0f70c0674664207
- https://git.kernel.org/stable/c/f30415929be8aeb002d557c8d3f7ab2d2188003a
- https://git.kernel.org/stable/c/f9d6cabff1fca010562dcdb0d22b296bdca3ba5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74492.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74492
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
