# [H] open_tree_attr: do not allow id-mapping changes without OPEN_TREE_CLONE

## Summary
Severity: High
Advisory: CVE-2025-39717
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39717
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

open_tree_attr: do not allow id-mapping changes without OPEN_TREE_CLONE

As described in commit 7a54947e727b ('Merge patch series "fs: allow
changing idmappings"'), open_tree_attr(2) was necessary in order to
allow for a detached mount to be created and have its idmappings changed
without the risk of any racing threads operating on it. For this reason,
mount_setattr(2) still does not allow for id-mappings to be changed.

However, there was a bug in commit 2462651ffa76 ("fs: allow changing
idmappings") which allowed users to bypass this restriction by calling
open_tree_attr(2) *without* OPEN_TREE_CLONE.

can_idmap_mount() prevented this bug from allowing an attached
mountpoint's id-mapping from being modified (thanks to an is_anon_ns()
check), but this still allows for detached (but visible) mounts to have
their be id-mapping changed. This risks the same UAF and locking issues
as described in the merge commit, and was likely unintentional.

## References
- https://git.kernel.org/stable/c/69dbdc711d9130136824e3830191a6afffa0a1f0
- https://git.kernel.org/stable/c/9308366f062129d52e0ee3f7a019f7dd41db33df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39717.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39717
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
