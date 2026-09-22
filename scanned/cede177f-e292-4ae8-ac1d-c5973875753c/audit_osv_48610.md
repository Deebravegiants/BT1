# [M] CVE-2018-1000200

## Summary
Severity: Medium
Advisory: CVE-2018-1000200
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2018-1000200
Type: osv

## Details
The Linux Kernel versions 4.14, 4.15, and 4.16 has a null pointer dereference which can result in an out of memory (OOM) killing of large mlocked processes. The issue arises from an oom killed process's final thread calling exit_mmap(), which calls munlock_vma_pages_all() for mlocked vmas.This can happen synchronously with the oom reaper's unmap_page_range() since the vma's VM_LOCKED bit is cleared before munlocking (to determine if any other vmas share the memory and are mlocked).

## References
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3752-3/
- https://marc.info/?l=linux-kernel&m=152460926619256
- https://access.redhat.com/security/cve/cve-2018-1000200
- https://marc.info/?l=linux-kernel&m=152400522806945
- http://seclists.org/oss-sec/2018/q2/67
- http://www.securityfocus.com/bid/104397
- https://access.redhat.com/errata/RHSA-2018:2948
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=27ae357fa82be5ab73b2ef8d39dcb8ca2563483a
