# [H] blk-cgroup: dropping parent refcount after pd_free_fn() is done

## Summary
Severity: High
Advisory: CVE-2023-54107
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54107
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-cgroup: dropping parent refcount after pd_free_fn() is done

Some cgroup policies will access parent pd through child pd even
after pd_offline_fn() is done. If pd_free_fn() for parent is called
before child, then UAF can be triggered. Hence it's better to guarantee
the order of pd_free_fn().

Currently refcount of parent blkg is dropped in __blkg_release(), which
is before pd_free_fn() is called in blkg_free_work_fn() while
blkg_free_work_fn() is called asynchronously.

This patch make sure pd_free_fn() called from removing cgroup is ordered
by delaying dropping parent refcount after calling pd_free_fn() for
child.

BTW, pd_free_fn() will also be called from blkcg_deactivate_policy()
from deleting device, and following patches will guarantee the order.

## References
- https://git.kernel.org/stable/c/c7241babf0855d8a6180cd1743ff0ec34de40b4e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54107.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54107
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
