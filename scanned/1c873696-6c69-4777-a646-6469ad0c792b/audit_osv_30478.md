# [H] net/sched: stop qdisc_tree_reduce_backlog on TC_H_ROOT

## Summary
Severity: High
Advisory: CVE-2024-53057
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53057
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: stop qdisc_tree_reduce_backlog on TC_H_ROOT

In qdisc_tree_reduce_backlog, Qdiscs with major handle ffff: are assumed
to be either root or ingress. This assumption is bogus since it's valid
to create egress qdiscs with major handle ffff:
Budimir Markovic found that for qdiscs like DRR that maintain an active
class list, it will cause a UAF with a dangling class pointer.

In 066a3b5b2346, the concern was to avoid iterating over the ingress
qdisc since its parent is itself. The proper fix is to stop when parent
TC_H_ROOT is reached because the only way to retrieve ingress is when a
hierarchy which does not contain a ffff: major handle call into
qdisc_lookup with TC_H_MAJ(TC_H_ROOT).

In the scenario where major ffff: is an egress qdisc in any of the tree
levels, the updates will also propagate to TC_H_ROOT, which then the
iteration must stop.


 net/sched/sch_api.c | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://git.kernel.org/stable/c/05df1b1dff8f197f1c275b57ccb2ca33021df552
- https://git.kernel.org/stable/c/2e95c4384438adeaa772caa560244b1a2efef816
- https://git.kernel.org/stable/c/580b3189c1972aff0f993837567d36392e9d981b
- https://git.kernel.org/stable/c/597cf9748c3477bf61bc35f0634129f56764ad24
- https://git.kernel.org/stable/c/9995909615c3431a5304c1210face5f268d24dba
- https://git.kernel.org/stable/c/ce691c814bc7a3c30c220ffb5b7422715458fd9b
- https://git.kernel.org/stable/c/dbe778b08b5101df9e89bc06e0a3a7ecd2f4ef20
- https://git.kernel.org/stable/c/e7f9a6f97eb067599a74f3bcb6761976b0ed303e
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53057.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53057
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
