# [M] CVE-2024-45780

## Summary
Severity: Medium
Advisory: CVE-2024-45780
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2024-45780
Type: osv

## Details
A flaw was found in grub2. When reading tar files, grub2 allocates an internal buffer for the file name. However, it fails to properly verify the allocation against possible integer overflows. It's possible to cause the allocation length to overflow with a crafted tar file, leading to a heap out-of-bounds write. This flaw eventually allows an attacker to circumvent secure boot protections.

## References
- https://access.redhat.com/security/cve/CVE-2024-45780
- https://bugzilla.redhat.com/show_bug.cgi?id=2345856
- https://lists.gnu.org/archive/html/grub-devel/2025-02/msg00024.html
