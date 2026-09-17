# [H] nilfs2: fix sysfs interface lifetime

## Summary
Severity: High
Advisory: CVE-2023-53440
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53440
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <4.14.313, >=4.15.0 <4.19.281, >=4.20.0 <5.4.241, >=5.5.0 <5.10.178, >=5.11.0 <5.15.107, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix sysfs interface lifetime

The current nilfs2 sysfs support has issues with the timing of creation
and deletion of sysfs entries, potentially leading to null pointer
dereferences, use-after-free, and lockdep warnings.

Some of the sysfs attributes for nilfs2 per-filesystem instance refer to
metadata file "cpfile", "sufile", or "dat", but
nilfs_sysfs_create_device_group that creates those attributes is executed
before the inodes for these metadata files are loaded, and
nilfs_sysfs_delete_device_group which deletes these sysfs entries is
called after releasing their metadata file inodes.

Therefore, access to some of these sysfs attributes may occur outside of
the lifetime of these metadata files, resulting in inode NULL pointer
dereferences or use-after-free.

In addition, the call to nilfs_sysfs_create_device_group() is made during
the locking period of the semaphore "ns_sem" of nilfs object, so the
shrinker call caused by the memory allocation for the sysfs entries, may
derive lock dependencies "ns_sem" -> (shrinker) -> "locks acquired in
nilfs_evict_inode()".

Since nilfs2 may acquire "ns_sem" deep in the call stack holding other
locks via its error handler __nilfs_error(), this causes lockdep to report
circular locking.  This is a false positive and no circular locking
actually occurs as no inodes exist yet when
nilfs_sysfs_create_device_group() is called.  Fortunately, the lockdep
warnings can be resolved by simply moving the call to
nilfs_sysfs_create_device_group() out of "ns_sem".

This fixes these sysfs issues by revising where the device's sysfs
interface is created/deleted and keeping its lifetime within the lifetime
of the metadata files above.

## References
- https://git.kernel.org/stable/c/1942ccb7d95f287a312fcbabfa8bc9ba501b1953
- https://git.kernel.org/stable/c/3dbee84bf9e3273c4bb9ca6fc18ff22fba23dd24
- https://git.kernel.org/stable/c/42560f9c92cc43dce75dbf06cc0d840dced39b12
- https://git.kernel.org/stable/c/5fe0ea141fbb887d407f1bf572ebf24427480d5c
- https://git.kernel.org/stable/c/83b16a60e413148685739635901937e2f16a7873
- https://git.kernel.org/stable/c/d20dcec8f326deb77b6688f8441e014045dac457
- https://git.kernel.org/stable/c/d540aea451ab5489777a8156560f1388449b3109
- https://git.kernel.org/stable/c/daf4eb3a908b108279b60172d2f176e70d2df875
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53440.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53440
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
