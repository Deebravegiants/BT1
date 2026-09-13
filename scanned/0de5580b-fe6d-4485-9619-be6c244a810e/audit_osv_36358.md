# [H] erofs: fix UAF issue for file-backed mounts w/ directio option

## Summary
Severity: High
Advisory: CVE-2026-23224
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-23224
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.72, >=6.13.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix UAF issue for file-backed mounts w/ directio option

[    9.269940][ T3222] Call trace:
[    9.269948][ T3222]  ext4_file_read_iter+0xac/0x108
[    9.269979][ T3222]  vfs_iocb_iter_read+0xac/0x198
[    9.269993][ T3222]  erofs_fileio_rq_submit+0x12c/0x180
[    9.270008][ T3222]  erofs_fileio_submit_bio+0x14/0x24
[    9.270030][ T3222]  z_erofs_runqueue+0x834/0x8ac
[    9.270054][ T3222]  z_erofs_read_folio+0x120/0x220
[    9.270083][ T3222]  filemap_read_folio+0x60/0x120
[    9.270102][ T3222]  filemap_fault+0xcac/0x1060
[    9.270119][ T3222]  do_pte_missing+0x2d8/0x1554
[    9.270131][ T3222]  handle_mm_fault+0x5ec/0x70c
[    9.270142][ T3222]  do_page_fault+0x178/0x88c
[    9.270167][ T3222]  do_translation_fault+0x38/0x54
[    9.270183][ T3222]  do_mem_abort+0x54/0xac
[    9.270208][ T3222]  el0_da+0x44/0x7c
[    9.270227][ T3222]  el0t_64_sync_handler+0x5c/0xf4
[    9.270253][ T3222]  el0t_64_sync+0x1bc/0x1c0

EROFS may encounter above panic when enabling file-backed mount w/
directio mount option, the root cause is it may suffer UAF in below
race condition:

- z_erofs_read_folio                          wq s_dio_done_wq
 - z_erofs_runqueue
  - erofs_fileio_submit_bio
   - erofs_fileio_rq_submit
    - vfs_iocb_iter_read
     - ext4_file_read_iter
      - ext4_dio_read_iter
       - iomap_dio_rw
       : bio was submitted and return -EIOCBQUEUED
                                              - dio_aio_complete_work
                                               - dio_complete
                                                - dio->iocb->ki_complete (erofs_fileio_ki_complete())
                                                 - kfree(rq)
                                                 : it frees iocb, iocb.ki_filp can be UAF in file_accessed().
       - file_accessed
       : access NULL file point

Introduce a reference count in struct erofs_fileio_rq, and initialize it
as two, both erofs_fileio_ki_complete() and erofs_fileio_rq_submit() will
decrease reference count, the last one decreasing the reference count
to zero will free rq.

## References
- https://git.kernel.org/stable/c/1caf50ce4af096d0280d59a31abdd85703cd995c
- https://git.kernel.org/stable/c/ae385826840a3c8e09bf38cac90adcd690716f57
- https://git.kernel.org/stable/c/b2ee5e4d5446babd23ff7beb4e636be0fb3ea5aa
- https://git.kernel.org/stable/c/d741534302f71c511eb0bb670b92eaa7df4a0aec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23224.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23224
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
