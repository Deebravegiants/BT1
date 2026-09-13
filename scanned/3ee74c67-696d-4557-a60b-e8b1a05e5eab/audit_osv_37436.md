# [H] ocfs2: fix possible deadlock between unlink and dio_end_io_write

## Summary
Severity: High
Advisory: CVE-2026-31598
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31598
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix possible deadlock between unlink and dio_end_io_write

ocfs2_unlink takes orphan dir inode_lock first and then ip_alloc_sem,
while in ocfs2_dio_end_io_write, it acquires these locks in reverse order.
This creates an ABBA lock ordering violation on lock classes
ocfs2_sysfile_lock_key[ORPHAN_DIR_SYSTEM_INODE] and
ocfs2_file_ip_alloc_sem_key.

Lock Chain #0 (orphan dir inode_lock -> ip_alloc_sem):
ocfs2_unlink
  ocfs2_prepare_orphan_dir
    ocfs2_lookup_lock_orphan_dir
      inode_lock(orphan_dir_inode) <- lock A
    __ocfs2_prepare_orphan_dir
      ocfs2_prepare_dir_for_insert
        ocfs2_extend_dir
	  ocfs2_expand_inline_dir
	    down_write(&oi->ip_alloc_sem) <- Lock B

Lock Chain #1 (ip_alloc_sem -> orphan dir inode_lock):
ocfs2_dio_end_io_write
  down_write(&oi->ip_alloc_sem) <- Lock B
  ocfs2_del_inode_from_orphan()
    inode_lock(orphan_dir_inode) <- Lock A

Deadlock Scenario:
  CPU0 (unlink)                     CPU1 (dio_end_io_write)
  ------                            ------
  inode_lock(orphan_dir_inode)
                                    down_write(ip_alloc_sem)
  down_write(ip_alloc_sem)
                                    inode_lock(orphan_dir_inode)

Since ip_alloc_sem is to protect allocation changes, which is unrelated
with operations in ocfs2_del_inode_from_orphan.  So move
ocfs2_del_inode_from_orphan out of ip_alloc_sem to fix the deadlock.

## References
- https://git.kernel.org/stable/c/297d8d7bb6a2bf133d3a3636edbdf94101cbd719
- https://git.kernel.org/stable/c/2b884d52273c60c298bd570163e8053657bbaff6
- https://git.kernel.org/stable/c/32630dee18c6bb2175c8a865a474749492eaf19c
- https://git.kernel.org/stable/c/4b80b5a838a32437f2cae0662578bac216a2c51a
- https://git.kernel.org/stable/c/93f35419eb84d58820040642cb6e7528fe4aba7a
- https://git.kernel.org/stable/c/b02da26a992db0c0e2559acbda0fc48d4a2fd337
- https://git.kernel.org/stable/c/bc0fb5c7d54c78be43a536df0e20dee32adb27d3
- https://git.kernel.org/stable/c/e049f7a9bd80b7319590789ea5e1c523d6339d91
- https://git.kernel.org/stable/c/f9fb1a7b635849322e1d7b7b6b26389778ec8e82
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31598.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31598
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
