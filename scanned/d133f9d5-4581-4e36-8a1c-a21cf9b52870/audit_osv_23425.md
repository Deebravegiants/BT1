# [M] block: fix memory leak in disk_register_independent_access_ranges

## Summary
Severity: Medium
Advisory: CVE-2022-48753
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48753
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: fix memory leak in disk_register_independent_access_ranges

kobject_init_and_add() takes reference even when it fails.
According to the doc of kobject_init_and_add()

   If this function returns an error, kobject_put() must be called to
   properly clean up the memory associated with the object.

Fix this issue by adding kobject_put().
Callback function blk_ia_ranges_sysfs_release() in kobject_put()
can handle the pointer "iars" properly.

## References
- https://git.kernel.org/stable/c/83114df32ae779df57e0af99a8ba6c3968b2ba3d
- https://git.kernel.org/stable/c/fe4214a07e0b53d2af711f57519e33739c5df23f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48753.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48753
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
