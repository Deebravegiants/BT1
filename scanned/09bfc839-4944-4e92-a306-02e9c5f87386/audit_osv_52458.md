# [H] CVE-2021-47470

## Summary
Severity: High
Advisory: CVE-2021-47470
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47470
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm, slub: fix potential use-after-free in slab_debugfs_fops

When sysfs_slab_add failed, we shouldn't call debugfs_slab_add() for s
because s will be freed soon.  And slab_debugfs_fops will use s later
leading to a use-after-free.

## References
- https://git.kernel.org/stable/c/159d8cfbd0428d487c53be4722f33cdab0d25d83
- https://git.kernel.org/stable/c/67823a544414def2a36c212abadb55b23bcda00c
