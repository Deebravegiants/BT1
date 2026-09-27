# [M] CVE-2023-52890

## Summary
Severity: Medium
Advisory: CVE-2023-52890
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-06-13
Source: https://osv.dev/vulnerability/CVE-2023-52890
Type: osv

## Details
NTFS-3G before 75dcdc2 has a use-after-free in ntfs_uppercase_mbs in libntfs-3g/unistr.c. NOTE: discussion suggests that exploitation would be challenging.

## References
- https://github.com/tuxera/ntfs-3g/issues/84
