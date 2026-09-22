# [M] CVE-2025-0686

## Summary
Severity: Medium
Advisory: CVE-2025-0686
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-0686
Type: osv

## Details
A flaw was found in grub2. When performing a symlink lookup from a romfs filesystem, grub's romfs filesystem module uses user-controlled parameters from the filesystem geometry to determine the internal buffer size, however, it improperly checks for integer overflows. A maliciously crafted filesystem may lead some of those buffer size calculations to overflow, causing it to perform a grub_malloc() operation with a smaller size than expected. As a result, the grub_romfs_read_symlink() may cause out-of-bounds writes when the calling grub_disk_read() function. This issue may be leveraged to corrupt grub's internal critical data and can result in arbitrary code execution by-passing secure boot protections.

## References
- https://access.redhat.com/security/cve/CVE-2025-0686
- https://bugzilla.redhat.com/show_bug.cgi?id=2346121
