# [H] eventfs: Fix use-after-free in eventfs_remove_rec()

## Summary
Severity: High
Advisory: CVE-2026-74606
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74606
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.152, >=6.7.0 <6.12.104, >=6.8.0 <6.18.45, >=6.13.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

eventfs: Fix use-after-free in eventfs_remove_rec()

eventfs_remove_rec() recursively removes the child at the current loop
position. After the recursive call returns, list_for_each_entry() advances
by reading list.next from the removed child.

If free_ei() drops the final reference, release_ei() reuses the list/rcu
union to queue an SRCU callback. The child may be freed before that read.
The eventfs_mutex serializes list updates, but it does not keep the removed
child alive or prevent the SRCU callback from running.

Use list_for_each_entry_safe() to save the next sibling before recursively
removing the current child.

## References
- https://git.kernel.org/stable/c/5635211b44969f4816e29ec4d5f8665fb39535d0
- https://git.kernel.org/stable/c/74bb1eaf72d185a78c879eb2678ea500f82f46a8
- https://git.kernel.org/stable/c/b77581b25e213e83b79ce11eb30024e55ceeb3e9
- https://git.kernel.org/stable/c/f161d7861a0bfdf10af6b738b3b57636204661fb
- https://git.kernel.org/stable/c/fd73b691702170d37d66f4b0278530cea8ed419a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74606.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74606
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
