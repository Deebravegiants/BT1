# [H] sched/fair: Fix potential memory corruption in child_cfs_rq_on_list

## Summary
Severity: High
Advisory: CVE-2025-21919
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21919
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched/fair: Fix potential memory corruption in child_cfs_rq_on_list

child_cfs_rq_on_list attempts to convert a 'prev' pointer to a cfs_rq.
This 'prev' pointer can originate from struct rq's leaf_cfs_rq_list,
making the conversion invalid and potentially leading to memory
corruption. Depending on the relative positions of leaf_cfs_rq_list and
the task group (tg) pointer within the struct, this can cause a memory
fault or access garbage data.

The issue arises in list_add_leaf_cfs_rq, where both
cfs_rq->leaf_cfs_rq_list and rq->leaf_cfs_rq_list are added to the same
leaf list. Also, rq->tmp_alone_branch can be set to rq->leaf_cfs_rq_list.

This adds a check `if (prev == &rq->leaf_cfs_rq_list)` after the main
conditional in child_cfs_rq_on_list. This ensures that the container_of
operation will convert a correct cfs_rq struct.

This check is sufficient because only cfs_rqs on the same CPU are added
to the list, so verifying the 'prev' pointer against the current rq's list
head is enough.

Fixes a potential memory corruption issue that due to current struct
layout might not be manifesting as a crash but could lead to unpredictable
behavior when the layout changes.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/000c9ee43928f2ce68a156dd40bab7616256f4dd
- https://git.kernel.org/stable/c/3b4035ddbfc8e4521f85569998a7569668cccf51
- https://git.kernel.org/stable/c/5cb300dcdd27e6a351ac02541e0231261c775852
- https://git.kernel.org/stable/c/9cc7f0018609f75a349e42e3aebc3b0e905ba775
- https://git.kernel.org/stable/c/b5741e4b9ef3567613b2351384f91d3f16e59986
- https://git.kernel.org/stable/c/e1dd09df30ba86716cb2ffab97dc35195c01eb8f
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21919.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21919
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
