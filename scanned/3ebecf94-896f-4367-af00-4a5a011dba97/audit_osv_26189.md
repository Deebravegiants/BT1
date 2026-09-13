# [H] bpf: Defer the free of inner map when necessary

## Summary
Severity: High
Advisory: CVE-2023-52447
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2023-52447
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Defer the free of inner map when necessary

When updating or deleting an inner map in map array or map htab, the map
may still be accessed by non-sleepable program or sleepable program.
However bpf_map_fd_put_ptr() decreases the ref-counter of the inner map
directly through bpf_map_put(), if the ref-counter is the last one
(which is true for most cases), the inner map will be freed by
ops->map_free() in a kworker. But for now, most .map_free() callbacks
don't use synchronize_rcu() or its variants to wait for the elapse of a
RCU grace period, so after the invocation of ops->map_free completes,
the bpf program which is accessing the inner map may incur
use-after-free problem.

Fix the free of inner map by invoking bpf_map_free_deferred() after both
one RCU grace period and one tasks trace RCU grace period if the inner
map has been removed from the outer map before. The deferment is
accomplished by using call_rcu() or call_rcu_tasks_trace() when
releasing the last ref-counter of bpf map. The newly-added rcu_head
field in bpf_map shares the same storage space with work field to
reduce the size of bpf_map.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/37d98fb9c3144c0fddf7f6e99aece9927ac8dce6
- https://git.kernel.org/stable/c/62fca83303d608ad4fec3f7428c8685680bb01b0
- https://git.kernel.org/stable/c/876673364161da50eed6b472d746ef88242b2368
- https://git.kernel.org/stable/c/90c445799fd1dc214d7c6279c144e33a35e29ef2
- https://git.kernel.org/stable/c/bfd9b20c4862f41d4590fde11d70a5eeae53dcc5
- https://git.kernel.org/stable/c/f91cd728b10c51f6d4a39957ccd56d1e802fc8ee
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52447.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52447
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
