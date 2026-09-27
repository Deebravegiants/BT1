# [C] block: recompute nr_integrity_segments in blk_insert_cloned_request

## Summary
Severity: Critical
Advisory: CVE-2026-64232
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64232
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: recompute nr_integrity_segments in blk_insert_cloned_request

blk_insert_cloned_request() already recomputes nr_phys_segments
against the bottom queue, because "the queue settings related to
segment counting may differ from the original queue." The exact same
reasoning applies to integrity segments: a stacked driver's underlying
queue can have tighter virt_boundary_mask, seg_boundary_mask, or
max_segment_size than the top queue, in which case
blk_rq_count_integrity_sg() against the bottom queue produces a
different count than the cached rq->nr_integrity_segments inherited
from the source request by blk_rq_prep_clone().

When the cached count is lower than the bottom queue's actual count,
blk_rq_map_integrity_sg() trips

	BUG_ON(segments > rq->nr_integrity_segments);

on dispatch. The same families of stacked setups that motivated the
existing nr_phys_segments recompute -- dm-multipath fanning out to
nvme-rdma in particular -- can produce this.

Mirror the nr_phys_segments handling: when the request carries
integrity, recompute nr_integrity_segments against the bottom queue
and reject the request if it exceeds the bottom queue's
max_integrity_segments. blk_rq_count_integrity_sg() and
queue_max_integrity_segments() are both already available via
<linux/blk-integrity.h>, which blk-mq.c includes.

This closes a latent gap in the stacking contract and brings the
integrity-segment accounting in line with the existing
phys-segment accounting.

## References
- https://git.kernel.org/stable/c/0943f81e1b3176f27dbaf6db268fc69d8a94f0ba
- https://git.kernel.org/stable/c/2c6e6a18a37b905cb584eb0dda3ae482162a81ca
- https://git.kernel.org/stable/c/42929c98d044f126508baf54a65b0f87f932fa75
- https://git.kernel.org/stable/c/53a01bcc0242590eda4c452a5bd996f62457113b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64232.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64232
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
