# [H] net/mlx5e: fix a potential double-free in fs_any_create_groups

## Summary
Severity: High
Advisory: CVE-2023-52667
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52667
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: fix a potential double-free in fs_any_create_groups

When kcalloc() for ft->g succeeds but kvzalloc() for in fails,
fs_any_create_groups() will free ft->g. However, its caller
fs_any_create_table() will free ft->g again through calling
mlx5e_destroy_flow_table(), which will lead to a double-free.
Fix this by setting ft->g to NULL in fs_any_create_groups().

## References
- https://git.kernel.org/stable/c/2897c981ee63e1be5e530b1042484626a10b26d8
- https://git.kernel.org/stable/c/65a4ade8a6d205979292e88beeb6a626ddbd4779
- https://git.kernel.org/stable/c/72a729868592752b5a294d27453da264106983b1
- https://git.kernel.org/stable/c/aef855df7e1bbd5aa4484851561211500b22707e
- https://git.kernel.org/stable/c/b2fa86b2aceb4bc9ada51cea90f61546d7512cbe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52667.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52667
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
