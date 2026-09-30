# [M] block: Fix potential deadlock in blk_ia_range_sysfs_show()

## Summary
Severity: Medium
Advisory: CVE-2022-49406
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49406
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: Fix potential deadlock in blk_ia_range_sysfs_show()

When being read, a sysfs attribute is already protected against removal
with the kobject node active reference counter. As a result, in
blk_ia_range_sysfs_show(), there is no need to take the queue sysfs
lock when reading the value of a range attribute. Using the queue sysfs
lock in this function creates a potential deadlock situation with the
disk removal, something that a lockdep signals with a splat when the
device is removed:

[  760.703551]  Possible unsafe locking scenario:
[  760.703551]
[  760.703554]        CPU0                    CPU1
[  760.703556]        ----                    ----
[  760.703558]   lock(&q->sysfs_lock);
[  760.703565]                                lock(kn->active#385);
[  760.703573]                                lock(&q->sysfs_lock);
[  760.703579]   lock(kn->active#385);
[  760.703587]
[  760.703587]  *** DEADLOCK ***

Solve this by removing the mutex_lock()/mutex_unlock() calls from
blk_ia_range_sysfs_show().

## References
- https://git.kernel.org/stable/c/41e46b3c2aa24f755b2ae9ec4ce931ba5f0d8532
- https://git.kernel.org/stable/c/717b078bc745ba9a262abebed9806a17e8bbb77b
- https://git.kernel.org/stable/c/dc107c805cde709866b59867ef72b9390199205e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49406.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49406
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
