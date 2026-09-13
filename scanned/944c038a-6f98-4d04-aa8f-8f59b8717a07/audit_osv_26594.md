# [H] NFSD: fix leaked reference count of nfsd4_ssc_umount_item

## Summary
Severity: High
Advisory: CVE-2023-53381
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53381
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.154, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: fix leaked reference count of nfsd4_ssc_umount_item

The reference count of nfsd4_ssc_umount_item is not decremented
on error conditions. This prevents the laundromat from unmounting
the vfsmount of the source file.

This patch decrements the reference count of nfsd4_ssc_umount_item
on error.

## References
- https://git.kernel.org/stable/c/2da50149981d05955e51c28e982e9ac29bd73417
- https://git.kernel.org/stable/c/34e8f9ec4c9ac235f917747b23a200a5e0ec857b
- https://git.kernel.org/stable/c/6c3c05402547aaca3edb23327b50f01a881831b9
- https://git.kernel.org/stable/c/80a15dc4a0214b55ca42675bb0bb2a8d857eb1d0
- https://git.kernel.org/stable/c/9f0df37520a27ad99eaacf38418b3d2bb5023105
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53381.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53381
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
