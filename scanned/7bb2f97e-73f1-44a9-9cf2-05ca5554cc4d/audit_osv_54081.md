# [C] CVE-2023-38430

## Summary
Severity: Critical
Advisory: CVE-2023-38430
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2023-38430
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.9. ksmbd does not validate the SMB request protocol ID, leading to an out-of-bounds read.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.9
- https://security.netapp.com/advisory/ntap-20230831-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/fs/smb/server?id=1c1bcf2d3ea061613119b534f57507c377df20f9
