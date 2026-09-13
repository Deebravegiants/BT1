# [H] memcg: fix possible use-after-free in memcg_write_event_control()

## Summary
Severity: High
Advisory: CVE-2022-48988
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48988
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <4.14.302, >=4.15.0 <4.19.269, >=4.20.0 <5.4.227, >=5.5.0 <5.10.159, >=5.11.0 <5.15.83, >=5.16.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

memcg: fix possible use-after-free in memcg_write_event_control()

memcg_write_event_control() accesses the dentry->d_name of the specified
control fd to route the write call.  As a cgroup interface file can't be
renamed, it's safe to access d_name as long as the specified file is a
regular cgroup file.  Also, as these cgroup interface files can't be
removed before the directory, it's safe to access the parent too.

Prior to 347c4a874710 ("memcg: remove cgroup_event->cft"), there was a
call to __file_cft() which verified that the specified file is a regular
cgroupfs file before further accesses.  The cftype pointer returned from
__file_cft() was no longer necessary and the commit inadvertently dropped
the file type check with it allowing any file to slip through.  With the
invarients broken, the d_name and parent accesses can now race against
renames and removals of arbitrary files and cause use-after-free's.

Fix the bug by resurrecting the file type check in __file_cft().  Now that
cgroupfs is implemented through kernfs, checking the file operations needs
to go through a layer of indirection.  Instead, let's check the superblock
and dentry type.

## References
- https://git.kernel.org/stable/c/0ed074317b835caa6c03bcfa8f133365324673dc
- https://git.kernel.org/stable/c/35963b31821920908e397146502066f6b032c917
- https://git.kernel.org/stable/c/4a7ba45b1a435e7097ca0f79a847d0949d0eb088
- https://git.kernel.org/stable/c/aad8bbd17a1d586005feb9226c2e9cfce1432e13
- https://git.kernel.org/stable/c/b77600e26fd48727a95ffd50ba1e937efb548125
- https://git.kernel.org/stable/c/e1ae97624ecf400ea56c238bff23e5cd139df0b8
- https://git.kernel.org/stable/c/f1f7f36cf682fa59db15e2089039a2eeb58ff2ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48988.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
