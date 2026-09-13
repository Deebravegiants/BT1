# [M] fs: don't try and remove empty rbtree node

## Summary
Severity: Medium
Advisory: CVE-2024-50204
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50204
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: don't try and remove empty rbtree node

When copying a namespace we won't have added the new copy into the
namespace rbtree until after the copy succeeded. Calling free_mnt_ns()
will try to remove the copy from the rbtree which is invalid. Simply
free the namespace skeleton directly.

## References
- https://git.kernel.org/stable/c/229fd15908fe1f99b1de4cde3326e62d1e892611
- https://git.kernel.org/stable/c/a8b155a2c30dc9a5ba837aa5fcba9a47cc031a9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50204.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50204
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
