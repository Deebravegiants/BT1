# [H] kernfs: Fix UAF in polling when open file is released

## Summary
Severity: High
Advisory: CVE-2025-39881
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39881
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.153, >=6.2.0 <6.6.107, >=6.7.0 <6.12.48, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

kernfs: Fix UAF in polling when open file is released

A use-after-free (UAF) vulnerability was identified in the PSI (Pressure
Stall Information) monitoring mechanism:

BUG: KASAN: slab-use-after-free in psi_trigger_poll+0x3c/0x140
Read of size 8 at addr ffff3de3d50bd308 by task systemd/1

psi_trigger_poll+0x3c/0x140
cgroup_pressure_poll+0x70/0xa0
cgroup_file_poll+0x8c/0x100
kernfs_fop_poll+0x11c/0x1c0
ep_item_poll.isra.0+0x188/0x2c0

Allocated by task 1:
cgroup_file_open+0x88/0x388
kernfs_fop_open+0x73c/0xaf0
do_dentry_open+0x5fc/0x1200
vfs_open+0xa0/0x3f0
do_open+0x7e8/0xd08
path_openat+0x2fc/0x6b0
do_filp_open+0x174/0x368

Freed by task 8462:
cgroup_file_release+0x130/0x1f8
kernfs_drain_open_files+0x17c/0x440
kernfs_drain+0x2dc/0x360
kernfs_show+0x1b8/0x288
cgroup_file_show+0x150/0x268
cgroup_pressure_write+0x1dc/0x340
cgroup_file_write+0x274/0x548

Reproduction Steps:
1. Open test/cpu.pressure and establish epoll monitoring
2. Disable monitoring: echo 0 > test/cgroup.pressure
3. Re-enable monitoring: echo 1 > test/cgroup.pressure

The race condition occurs because:
1. When cgroup.pressure is disabled (echo 0 > cgroup.pressure), it:
   - Releases PSI triggers via cgroup_file_release()
   - Frees of->priv through kernfs_drain_open_files()
2. While epoll still holds reference to the file and continues polling
3. Re-enabling (echo 1 > cgroup.pressure) accesses freed of->priv

epolling			disable/enable cgroup.pressure
fd=open(cpu.pressure)
while(1)
...
epoll_wait
kernfs_fop_poll
kernfs_get_active = true	echo 0 > cgroup.pressure
...				cgroup_file_show
				kernfs_show
				// inactive kn
				kernfs_drain_open_files
				cft->release(of);
				kfree(ctx);
				...
kernfs_get_active = false
				echo 1 > cgroup.pressure
				kernfs_show
				kernfs_activate_one(kn);
kernfs_fop_poll
kernfs_get_active = true
cgroup_file_poll
psi_trigger_poll
// UAF
...
end: close(fd)

To address this issue, introduce kernfs_get_active_of() for kernfs open
files to obtain active references. This function will fail if the open file
has been released. Replace kernfs_get_active() with kernfs_get_active_of()
to prevent further operations on released file descriptors.

## References
- https://git.kernel.org/stable/c/34d9cafd469c69ad85e6a36b4303c78382cf5c79
- https://git.kernel.org/stable/c/3c9ba2777d6c86025e1ba4186dc5cd930e40ec5f
- https://git.kernel.org/stable/c/7e64474aba78d240f7804f48f2d454dcca78b15f
- https://git.kernel.org/stable/c/854baafc00c433cccbe0ab4231b77aeb9b637b77
- https://git.kernel.org/stable/c/ac5cda4fae8818cf1963317bb699f7f2f85b60af
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39881.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39881
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
