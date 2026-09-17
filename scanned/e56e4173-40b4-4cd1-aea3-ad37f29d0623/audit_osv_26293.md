# [H] gfs2: Fix slab-use-after-free in gfs2_qd_dealloc

## Summary
Severity: High
Advisory: CVE-2023-52760
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52760
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: Fix slab-use-after-free in gfs2_qd_dealloc

In gfs2_put_super(), whether withdrawn or not, the quota should
be cleaned up by gfs2_quota_cleanup().

Otherwise, struct gfs2_sbd will be freed before gfs2_qd_dealloc (rcu
callback) has run for all gfs2_quota_data objects, resulting in
use-after-free.

Also, gfs2_destroy_threads() and gfs2_quota_cleanup() is already called
by gfs2_make_fs_ro(), so in gfs2_put_super(), after calling
gfs2_make_fs_ro(), there is no need to call them again.

## References
- https://git.kernel.org/stable/c/08a28272faa750d4357ea2cb48d2baefd778ea81
- https://git.kernel.org/stable/c/7ad4e0a4f61c57c3ca291ee010a9d677d0199fba
- https://git.kernel.org/stable/c/bdcb8aa434c6d36b5c215d02a9ef07551be25a37
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52760.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52760
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
