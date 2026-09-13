# [H] CVE-2025-1125

## Summary
Severity: High
Advisory: CVE-2025-1125
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-1125
Type: osv

## Details
When reading data from a hfs filesystem, grub's hfs filesystem module uses user-controlled parameters from the filesystem metadata to calculate the internal buffers size, however it misses to properly check for integer overflows. A maliciouly crafted filesystem may lead some of those buffer size calculation to overflow, causing it to perform a grub_malloc() operation with a smaller size than expected. As a result the hfsplus_open_compressed_real() function will write past of the internal buffer length. This flaw may be leveraged to corrupt grub's internal critical data and may result in arbitrary code execution by-passing secure boot protections.

## References
- https://access.redhat.com/security/cve/CVE-2025-1125
- https://lists.gnu.org/archive/html/grub-devel/2025-02/msg00024.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2346138
