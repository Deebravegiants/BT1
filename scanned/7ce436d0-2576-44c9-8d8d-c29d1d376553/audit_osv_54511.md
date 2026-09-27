# [H] CVE-2024-0562

## Summary
Severity: High
Advisory: CVE-2024-0562
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-15
Source: https://osv.dev/vulnerability/CVE-2024-0562
Type: osv

## Details
A use-after-free flaw was found in the Linux Kernel. When a disk is removed, bdi_unregister is called to stop further write-back and waits for associated delayed work to complete. However, wb_inode_writeback_end() may schedule bandwidth estimation work after this has completed, which can result in the timer attempting to access the recently freed bdi_writeback.

## References
- https://access.redhat.com/errata/RHSA-2024:0412
- https://access.redhat.com/security/cve/CVE-2024-0562
- https://bugzilla.redhat.com/show_bug.cgi?id=2258475
- https://patchwork.kernel.org/project/linux-mm/patch/20220801155034.3772543-1-khazhy@google.com/
