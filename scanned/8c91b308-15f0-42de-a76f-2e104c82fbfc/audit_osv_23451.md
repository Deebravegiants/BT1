# [H] usb: f_fs: Fix use-after-free for epfile

## Summary
Severity: High
Advisory: CVE-2022-48822
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48822
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.14.267, >=4.15.0 <4.19.230, >=4.20.0 <5.4.180, >=5.5.0 <5.10.101, >=5.11.0 <5.15.24, >=5.16.0 <5.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: f_fs: Fix use-after-free for epfile

Consider a case where ffs_func_eps_disable is called from
ffs_func_disable as part of composition switch and at the
same time ffs_epfile_release get called from userspace.
ffs_epfile_release will free up the read buffer and call
ffs_data_closed which in turn destroys ffs->epfiles and
mark it as NULL. While this was happening the driver has
already initialized the local epfile in ffs_func_eps_disable
which is now freed and waiting to acquire the spinlock. Once
spinlock is acquired the driver proceeds with the stale value
of epfile and tries to free the already freed read buffer
causing use-after-free.

Following is the illustration of the race:

      CPU1                                  CPU2

   ffs_func_eps_disable
   epfiles (local copy)
					ffs_epfile_release
					ffs_data_closed
					if (last file closed)
					ffs_data_reset
					ffs_data_clear
					ffs_epfiles_destroy
spin_lock
dereference epfiles

Fix this races by taking epfiles local copy & assigning it under
spinlock and if epfiles(local) is null then update it in ffs->epfiles
then finally destroy it.
Extending the scope further from the race, protecting the ep related
structures, and concurrent accesses.

## References
- https://git.kernel.org/stable/c/0042178a69eb77a979e36a50dcce9794a3140ef8
- https://git.kernel.org/stable/c/32048f4be071f9a6966744243f1786f45bb22dc2
- https://git.kernel.org/stable/c/3e078b18753669615301d946297bafd69294ad2c
- https://git.kernel.org/stable/c/72a8aee863af099d4434314c4536d6c9a61dcf3c
- https://git.kernel.org/stable/c/c9fc422c9a43e3d58d246334a71f3390401781dc
- https://git.kernel.org/stable/c/cfe5f6fd335d882bcc829a1c8a7d462a455c626e
- https://git.kernel.org/stable/c/ebe2b1add1055b903e2acd86b290a85297edc0b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48822.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48822
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
