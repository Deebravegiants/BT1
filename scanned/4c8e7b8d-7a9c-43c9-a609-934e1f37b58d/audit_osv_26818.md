# [H] blk-cgroup: hold queue_lock when removing blkg->q_node

## Summary
Severity: High
Advisory: CVE-2023-54088
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54088
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.17, >=6.2.0 <6.2.4, >=6.3.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-cgroup: hold queue_lock when removing blkg->q_node

When blkg is removed from q->blkg_list from blkg_free_workfn(), queue_lock
has to be held, otherwise, all kinds of bugs(list corruption, hard lockup,
..) can be triggered from blkg_destroy_all().

## References
- https://git.kernel.org/stable/c/083b58373463a6e5ee60ecb135269348f68ad7df
- https://git.kernel.org/stable/c/b5dae1cd0d8368b4338430ff93403df67f0b8bcc
- https://git.kernel.org/stable/c/c164c7bc9775be7bcc68754bb3431fce5823822e
- https://git.kernel.org/stable/c/cd4ffdf56791eec95af01f06bee1ec7665ca75c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54088.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54088
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
