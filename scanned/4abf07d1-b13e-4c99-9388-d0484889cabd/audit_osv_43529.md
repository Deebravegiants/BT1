# [H] btrfs: fix invalid pointer dereference in __btrfs_run_delayed_refs()

## Summary
Severity: High
Advisory: CVE-2026-74321
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74321
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix invalid pointer dereference in __btrfs_run_delayed_refs()

In the beginning of the loop, we try to obtain a locked delayed ref head,
if 'locked_ref' is currently NULL, by calling btrfs_select_ref_head(),
which can return an error pointer. If the error pointer is -EAGAIN we do
a continue and go back to the beginning of the loop, which will not try
again to call btrfs_select_ref_head() since 'locked_ref' is no longer
NULL but it's ERR_PTR(-EAGAIN), and then we do:

   spin_lock(&locked_ref->lock);

against a ERR_PTR(-EAGAIN) value, generating an invalid pointer
dereference.

Fix this by ensuring that 'locked_ref' is set to NULL when
btrfs_select_ref_head() returns ERR_PTR(-EAGAIN) and incrementing 'count'
as well, to prevent infinite looping. We do this by doing a goto to the
bottom of the loop that already sets 'locked_ref' to NULL and does a
cond_resched(), with an increment to 'count' right before the goto.
These measures were in place before the refactoring in commit 0110a4c43451
("btrfs: refactor __btrfs_run_delayed_refs loop") but were unintentionally
lost afterwards.

## References
- https://git.kernel.org/stable/c/015dc4a1e0c2cba551d4620eba13d26d5081dc34
- https://git.kernel.org/stable/c/3b15d02be05e74321adb1e0ae0cb4ccfba7c6cb1
- https://git.kernel.org/stable/c/486f8298b6188ff11ef1f4be7f1d5d2e4d1b1fae
- https://git.kernel.org/stable/c/65770111a2d47c2b15e20b2ba92bb12198f289d4
- https://git.kernel.org/stable/c/9faa6b69ad73f03c7bde53e07d75a28822dc9a1a
- https://git.kernel.org/stable/c/a71143590ce9764dbcb47617647592ff8b4d48bc
- https://git.kernel.org/stable/c/ba9fa2ff5981589bb49094d3358c339b37c47f53
- https://git.kernel.org/stable/c/c372ca227e16bace86f1df1fa4ae6849e2fcfa28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74321.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74321
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
