# [H] eventfs: Use children field for rcu head and add memory barriers

## Summary
Severity: High
Advisory: CVE-2026-74605
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74605
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

eventfs: Use children field for rcu head and add memory barriers

When an eventfs inode is freed, it sets ei->is_freed and then uses its
ei->list to add it to the srcu link list as the list field is a union with
the rcu list head. As the ei->list is used to iterate over an SRCU
protected list without taking the eventfs_mutex, there's nothing stopping
the iteration over that list to see the ei->rcu instead of the ei->list
and it will read a corrupt target.

To fix this, change the union of the rcu list head with the children list.
On freeing the eventfs inode, set the is_free and execute a smp_wmb()
before adding the eventfs inode to the SRCU list.

On iteration of the ei->children list, at the start, execute a smp_rmb()
and then read the is_freed of the ei to see if the children list is still
valid. If is_freed is set, then the ei_child read is not valid and the
loop should exit immediately.

## References
- https://git.kernel.org/stable/c/004f7232e49730448f91665e76bdd7dff8e0c638
- https://git.kernel.org/stable/c/f0ece16ffca7384787b692431961ce202907acf5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74605.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74605
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
