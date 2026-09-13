# [H] cifs: Fix the smbd_response slab to allow usercopy

## Summary
Severity: High
Advisory: CVE-2025-38523
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38523
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.36, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix the smbd_response slab to allow usercopy

The handling of received data in the smbdirect client code involves using
copy_to_iter() to copy data from the smbd_reponse struct's packet trailer
to a folioq buffer provided by netfslib that encapsulates a chunk of
pagecache.

If, however, CONFIG_HARDENED_USERCOPY=y, this will result in the checks
then performed in copy_to_iter() oopsing with something like the following:

 CIFS: Attempting to mount //172.31.9.1/test
 CIFS: VFS: RDMA transport established
 usercopy: Kernel memory exposure attempt detected from SLUB object 'smbd_response_0000000091e24ea1' (offset 81, size 63)!
 ------------[ cut here ]------------
 kernel BUG at mm/usercopy.c:102!
 ...
 RIP: 0010:usercopy_abort+0x6c/0x80
 ...
 Call Trace:
  <TASK>
  __check_heap_object+0xe3/0x120
  __check_object_size+0x4dc/0x6d0
  smbd_recv+0x77f/0xfe0 [cifs]
  cifs_readv_from_socket+0x276/0x8f0 [cifs]
  cifs_read_from_socket+0xcd/0x120 [cifs]
  cifs_demultiplex_thread+0x7e9/0x2d50 [cifs]
  kthread+0x396/0x830
  ret_from_fork+0x2b8/0x3b0
  ret_from_fork_asm+0x1a/0x30

The problem is that the smbd_response slab's packet field isn't marked as
being permitted for usercopy.

Fix this by passing parameters to kmem_slab_create() to indicate that
copy_to_iter() is permitted from the packet region of the smbd_response
slab objects, less the header space.

## References
- https://git.kernel.org/stable/c/43e7e284fc77b710d899569360ea46fa3374ae22
- https://git.kernel.org/stable/c/87dcc7e33fc3dcb8ed32333cec016528b5bb6ce4
- https://git.kernel.org/stable/c/f0dd353d47f7051afa98c6c60c7486831eb1a410
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38523.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38523
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
