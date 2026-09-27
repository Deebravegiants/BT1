# [M] CVE-2024-45779

## Summary
Severity: Medium
Advisory: CVE-2024-45779
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2024-45779
Type: osv

## Details
An integer overflow flaw was found in the BFS file system driver in grub2. When reading a file with an indirect extent map, grub2 fails to validate the number of extent entries to be read. A crafted or corrupted BFS filesystem may cause an integer overflow during the file reading, leading to a heap of bounds read. As a consequence, sensitive data may be leaked, or grub2 will crash.

## References
- https://access.redhat.com/security/cve/CVE-2024-45779
- https://bugzilla.redhat.com/show_bug.cgi?id=2345854
- https://lists.gnu.org/archive/html/grub-devel/2025-02/msg00024.html
