# [M] CVE-2021-47579

## Summary
Severity: Medium
Advisory: CVE-2021-47579
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47579
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovl: fix warning in ovl_create_real()

Syzbot triggered the following warning in ovl_workdir_create() ->
ovl_create_real():

	if (!err && WARN_ON(!newdentry->d_inode)) {

The reason is that the cgroup2 filesystem returns from mkdir without
instantiating the new dentry.

Weird filesystems such as this will be rejected by overlayfs at a later
stage during setup, but to prevent such a warning, call ovl_mkdir_real()
directly from ovl_workdir_create() and reject this case early.

## References
- https://git.kernel.org/stable/c/f9f300a92297be8250547347fd52216ef0177ae0
- https://git.kernel.org/stable/c/1f5573cfe7a7056e80a92c7a037a3e69f3a13d1c
- https://git.kernel.org/stable/c/445d2dc63e5871d218f21b8f62ab29ac72f2e6b8
- https://git.kernel.org/stable/c/6859985a2fbda5d1586bf44538853e1be69e85f7
- https://git.kernel.org/stable/c/d2ccdd4e4efab06178608a34d7bfb20a54104c02
