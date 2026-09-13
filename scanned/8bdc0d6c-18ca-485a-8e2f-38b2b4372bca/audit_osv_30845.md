# [H] scsi: sg: Fix slab-use-after-free read in sg_release()

## Summary
Severity: High
Advisory: CVE-2024-56631
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56631
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.127, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: sg: Fix slab-use-after-free read in sg_release()

Fix a use-after-free bug in sg_release(), detected by syzbot with KASAN:

BUG: KASAN: slab-use-after-free in lock_release+0x151/0xa30
kernel/locking/lockdep.c:5838
__mutex_unlock_slowpath+0xe2/0x750 kernel/locking/mutex.c:912
sg_release+0x1f4/0x2e0 drivers/scsi/sg.c:407

In sg_release(), the function kref_put(&sfp->f_ref, sg_remove_sfp) is
called before releasing the open_rel_lock mutex. The kref_put() call may
decrement the reference count of sfp to zero, triggering its cleanup
through sg_remove_sfp(). This cleanup includes scheduling deferred work
via sg_remove_sfp_usercontext(), which ultimately frees sfp.

After kref_put(), sg_release() continues to unlock open_rel_lock and may
reference sfp or sdp. If sfp has already been freed, this results in a
slab-use-after-free error.

Move the kref_put(&sfp->f_ref, sg_remove_sfp) call after unlocking the
open_rel_lock mutex. This ensures:

 - No references to sfp or sdp occur after the reference count is
   decremented.

 - Cleanup functions such as sg_remove_sfp() and
   sg_remove_sfp_usercontext() can safely execute without impacting the
   mutex handling in sg_release().

The fix has been tested and validated by syzbot. This patch closes the
bug reported at the following syzkaller link and ensures proper
sequencing of resource cleanup and mutex operations, eliminating the
risk of use-after-free errors in sg_release().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/198b89dd5a595ee3f96e5ce5c448b0484cd0e53c
- https://git.kernel.org/stable/c/1f5e2f1ca5875728fcf62bc1a054707444ab4960
- https://git.kernel.org/stable/c/275b8347e21ab8193e93223a8394a806e4ba8918
- https://git.kernel.org/stable/c/285ce1f89f8d414e7eecab5ef5118cd512596318
- https://git.kernel.org/stable/c/59b30afa578637169e2819536bb66459fdddc39d
- https://git.kernel.org/stable/c/e19acb1926c4a1f30ee1ec84d8afba2d975bd534
- https://git.kernel.org/stable/c/f10593ad9bc36921f623361c9e3dd96bd52d85ee
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56631.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56631
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
