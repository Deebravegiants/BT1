# [H] CVE-2024-45782

## Summary
Severity: High
Advisory: CVE-2024-45782
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2024-45782
Type: osv

## Details
A flaw was found in the HFS filesystem. When reading an HFS volume's name at grub_fs_mount(), the HFS filesystem driver performs a strcpy() using the user-provided volume name as input without properly validating the volume name's length. This issue may read to a heap-based out-of-bounds writer, impacting grub's sensitive data integrity and eventually leading to a secure boot protection bypass.

## References
- https://access.redhat.com/security/cve/CVE-2024-45782
- https://bugzilla.redhat.com/show_bug.cgi?id=2345858
