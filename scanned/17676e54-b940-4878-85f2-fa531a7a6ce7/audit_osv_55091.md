# [H] CVE-2025-0689

## Summary
Severity: High
Advisory: CVE-2025-0689
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-0689
Type: osv

## Details
When reading data from disk, the grub's UDF filesystem module utilizes the user controlled data length metadata to allocate its internal buffers. In certain scenarios, while iterating through disk sectors, it assumes the read size from the disk is always smaller than the allocated buffer size which is not guaranteed. A crafted filesystem image may lead to a heap-based buffer overflow resulting in critical data to be corrupted, resulting in the risk of arbitrary code execution by-passing secure boot protections.

## References
- https://lists.gnu.org/archive/html/grub-devel/2025-02/msg00024.html
- https://access.redhat.com/security/cve/CVE-2025-0689
- https://bugzilla.redhat.com/show_bug.cgi?id=2346122
