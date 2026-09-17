# [M] ext4: fix i_disksize exceeding i_size problem in paritally written case

## Summary
Severity: Medium
Advisory: CVE-2023-53270
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53270
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix i_disksize exceeding i_size problem in paritally written case

It is possible for i_disksize can exceed i_size, triggering a warning.

generic_perform_write
 copied = iov_iter_copy_from_user_atomic(len) // copied < len
 ext4_da_write_end
 | ext4_update_i_disksize
 |  new_i_size = pos + copied;
 |  WRITE_ONCE(EXT4_I(inode)->i_disksize, newsize) // update i_disksize
 | generic_write_end
 |  copied = block_write_end(copied, len) // copied = 0
 |   if (unlikely(copied < len))
 |    if (!PageUptodate(page))
 |     copied = 0;
 |  if (pos + copied > inode->i_size) // return false
 if (unlikely(copied == 0))
  goto again;
 if (unlikely(iov_iter_fault_in_readable(i, bytes))) {
  status = -EFAULT;
  break;
 }

We get i_disksize greater than i_size here, which could trigger WARNING
check 'i_size_read(inode) < EXT4_I(inode)->i_disksize' while doing dio:

ext4_dio_write_iter
 iomap_dio_rw
  __iomap_dio_rw // return err, length is not aligned to 512
 ext4_handle_inode_extension
  WARN_ON_ONCE(i_size_read(inode) < EXT4_I(inode)->i_disksize) // Oops

 WARNING: CPU: 2 PID: 2609 at fs/ext4/file.c:319
 CPU: 2 PID: 2609 Comm: aa Not tainted 6.3.0-rc2
 RIP: 0010:ext4_file_write_iter+0xbc7
 Call Trace:
  vfs_write+0x3b1
  ksys_write+0x77
  do_syscall_64+0x39

Fix it by updating 'copied' value before updating i_disksize just like
ext4_write_inline_data_end() does.

A reproducer can be found in the buganizer link below.

## References
- https://git.kernel.org/stable/c/18eb23891aeae3229baf8c7c23b76be3364e1967
- https://git.kernel.org/stable/c/1dedde690303c05ef732b7c5c8356fdf60a4ade3
- https://git.kernel.org/stable/c/3ecea2fee14227712694c8b54ad99d471e61de92
- https://git.kernel.org/stable/c/53877ed201baa6b58f7ce9df92664a839113c30e
- https://git.kernel.org/stable/c/d30090eb546d993ea3f3023452540c476ea614a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53270.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53270
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
