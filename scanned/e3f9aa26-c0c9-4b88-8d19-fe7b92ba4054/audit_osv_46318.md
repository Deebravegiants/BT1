# [C] smb: client: fix use-after-free in cifs_oplock_break

## Summary
Severity: Critical
Advisory: CVE-2025-38527
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38527
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix use-after-free in cifs_oplock_break

A race condition can occur in cifs_oplock_break() leading to a
use-after-free of the cinode structure when unmounting:

  cifs_oplock_break()
    _cifsFileInfo_put(cfile)
      cifsFileInfo_put_final()
        cifs_sb_deactive()
          [last ref, start releasing sb]
            kill_sb()
              kill_anon_super()
                generic_shutdown_super()
                  evict_inodes()
                    dispose_list()
                      evict()
                        destroy_inode()
                          call_rcu(&inode->i_rcu, i_callback)
    spin_lock(&cinode->open_file_lock)  <- OK
                            [later] i_callback()
                              cifs_free_inode()
                                kmem_cache_free(cinode)
    spin_unlock(&cinode->open_file_lock)  <- UAF
    cifs_done_oplock_break(cinode)       <- UAF

The issue occurs when umount has already released its reference to the
superblock. When _cifsFileInfo_put() calls cifs_sb_deactive(), this
releases the last reference, triggering the immediate cleanup of all
inodes under RCU. However, cifs_oplock_break() continues to access the
cinode after this point, resulting in use-after-free.

Fix this by holding an extra reference to the superblock during the
entire oplock break operation. This ensures that the superblock and
its inodes remain valid until the oplock break completes.

## References
- https://git.kernel.org/stable/c/09bce2138a30ef10d8821c8c3f73a4ab7a5726bc
- https://git.kernel.org/stable/c/0a4eec84d4d2c4085d4ed8630fd74e4b39033c1b
- https://git.kernel.org/stable/c/2baaf5bbab2ac474c4f92c10fcb3310f824db995
- https://git.kernel.org/stable/c/4256a483fe58af66a46cbf3dc48ff26e580d3308
- https://git.kernel.org/stable/c/705c79101ccf9edea5a00d761491a03ced314210
- https://git.kernel.org/stable/c/da11bd4b697b393a207f19a2ed7d382a811a3ddc
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38527.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38527
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
