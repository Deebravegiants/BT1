# [H] blk-cgroup: fix list corruption from reorder of WRITE ->lqueued

## Summary
Severity: High
Advisory: CVE-2024-38384
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-38384
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-cgroup: fix list corruption from reorder of WRITE ->lqueued

__blkcg_rstat_flush() can be run anytime, especially when blk_cgroup_bio_start
is being executed.

If WRITE of `->lqueued` is re-ordered with READ of 'bisc->lnode.next' in
the loop of __blkcg_rstat_flush(), `next_bisc` can be assigned with one
stat instance being added in blk_cgroup_bio_start(), then the local
list in __blkcg_rstat_flush() could be corrupted.

Fix the issue by adding one barrier.

## References
- https://git.kernel.org/stable/c/714e59b5456e4d6e4295a9968c564abe193f461c
- https://git.kernel.org/stable/c/785298ab6b802afa75089239266b6bbea590809c
- https://git.kernel.org/stable/c/d0aac2363549e12cc79b8e285f13d5a9f42fd08e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38384.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38384
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
