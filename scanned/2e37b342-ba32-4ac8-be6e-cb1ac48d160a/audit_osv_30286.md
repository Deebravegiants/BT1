# [H] dm cache: fix flushing uninitialized delayed_work on cache_ctr error

## Summary
Severity: High
Advisory: CVE-2024-50280
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50280
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.117, >=6.2.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm cache: fix flushing uninitialized delayed_work on cache_ctr error

An unexpected WARN_ON from flush_work() may occur when cache creation
fails, caused by destroying the uninitialized delayed_work waker in the
error path of cache_create(). For example, the warning appears on the
superblock checksum error.

Reproduce steps:

dmsetup create cmeta --table "0 8192 linear /dev/sdc 0"
dmsetup create cdata --table "0 65536 linear /dev/sdc 8192"
dmsetup create corig --table "0 524288 linear /dev/sdc 262144"
dd if=/dev/urandom of=/dev/mapper/cmeta bs=4k count=1 oflag=direct
dmsetup create cache --table "0 524288 cache /dev/mapper/cmeta \
/dev/mapper/cdata /dev/mapper/corig 128 2 metadata2 writethrough smq 0"

Kernel logs:

(snip)
WARNING: CPU: 0 PID: 84 at kernel/workqueue.c:4178 __flush_work+0x5d4/0x890

Fix by pulling out the cancel_delayed_work_sync() from the constructor's
error path. This patch doesn't affect the use-after-free fix for
concurrent dm_resume and dm_destroy (commit 6a459d8edbdb ("dm cache: Fix
UAF in destroy()")) as cache_dtr is not changed.

## References
- https://git.kernel.org/stable/c/135496c208ba26fd68cdef10b64ed7a91ac9a7ff
- https://git.kernel.org/stable/c/40fac0271c7aedf60d81ed8214e80851e5b26312
- https://git.kernel.org/stable/c/5a754d3c771280f2d06bf8ab716d6a0d36ca256e
- https://git.kernel.org/stable/c/8cc12dab635333c4ea28e72d7b947be7d0543c2c
- https://git.kernel.org/stable/c/aee3ecda73ce13af7c3e556383342b57e6bd0718
- https://git.kernel.org/stable/c/d154b333a5667b6c1b213a11a41ad7aaccd10c3d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50280.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
