# [M] net/mlx5e: fix memory leak in mlx5e_fs_tt_redirect_any_create

## Summary
Severity: Medium
Advisory: CVE-2023-53371
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53371
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: fix memory leak in mlx5e_fs_tt_redirect_any_create

The memory pointed to by the fs->any pointer is not freed in the error
path of mlx5e_fs_tt_redirect_any_create, which can lead to a memory leak.
Fix by freeing the memory in the error path, thereby making the error path
identical to mlx5e_fs_tt_redirect_any_destroy().

## References
- https://git.kernel.org/stable/c/3250affdc658557a41df9c5fb567723e421f8bf2
- https://git.kernel.org/stable/c/75df2fe6d160e16be880aacacd521b135d7177c9
- https://git.kernel.org/stable/c/8a75a6f169c3df3a94802314aa61282772ac75b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53371.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53371
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
