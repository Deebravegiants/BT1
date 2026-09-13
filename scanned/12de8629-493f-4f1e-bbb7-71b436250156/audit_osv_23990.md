# [H] nilfs2: fix use-after-free bug of ns_writer on remount

## Summary
Severity: High
Advisory: CVE-2022-49834
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49834
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <4.9.334, >=4.10.0 <4.14.300, >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.5.0 <5.10.155, >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix use-after-free bug of ns_writer on remount

If a nilfs2 filesystem is downgraded to read-only due to metadata
corruption on disk and is remounted read/write, or if emergency read-only
remount is performed, detaching a log writer and synchronizing the
filesystem can be done at the same time.

In these cases, use-after-free of the log writer (hereinafter
nilfs->ns_writer) can happen as shown in the scenario below:

 Task1                               Task2
 --------------------------------    ------------------------------
 nilfs_construct_segment
   nilfs_segctor_sync
     init_wait
     init_waitqueue_entry
     add_wait_queue
     schedule
                                     nilfs_remount (R/W remount case)
				       nilfs_attach_log_writer
                                         nilfs_detach_log_writer
                                           nilfs_segctor_destroy
                                             kfree
     finish_wait
       _raw_spin_lock_irqsave
         __raw_spin_lock_irqsave
           do_raw_spin_lock
             debug_spin_lock_before  <-- use-after-free

While Task1 is sleeping, nilfs->ns_writer is freed by Task2.  After Task1
waked up, Task1 accesses nilfs->ns_writer which is already freed.  This
scenario diagram is based on the Shigeru Yoshida's post [1].

This patch fixes the issue by not detaching nilfs->ns_writer on remount so
that this UAF race doesn't happen.  Along with this change, this patch
also inserts a few necessary read-only checks with superblock instance
where only the ns_writer pointer was used to check if the filesystem is
read-only.

## References
- https://git.kernel.org/stable/c/39a3ed68270b079c6b874d4e4727a512b9b4882c
- https://git.kernel.org/stable/c/4feedde5486c07ea79787839153a71ca71329c7d
- https://git.kernel.org/stable/c/8cccf05fe857a18ee26e20d11a8455a73ffd4efd
- https://git.kernel.org/stable/c/9b162e81045266a2d5b44df9dffdf05c54de9cca
- https://git.kernel.org/stable/c/afbd1188382a75f6cfe22c0b68533f7f9664f182
- https://git.kernel.org/stable/c/b152300d5a1ba4258dacf9916bff20e6a8c7603b
- https://git.kernel.org/stable/c/b2fbf10040216ef5ee270773755fc2f5da65b749
- https://git.kernel.org/stable/c/b4736ab5542112fe0a40f140a0a0b072954f34da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49834.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49834
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
