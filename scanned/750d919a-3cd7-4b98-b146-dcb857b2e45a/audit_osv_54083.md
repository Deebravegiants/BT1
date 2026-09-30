# [C] CVE-2023-38432

## Summary
Severity: Critical
Advisory: CVE-2023-38432
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2023-38432
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.10. fs/smb/server/smb2misc.c in ksmbd does not validate the relationship between the command payload size and the RFC1002 length specification, leading to an out-of-bounds read.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.10
- https://security.netapp.com/advisory/ntap-20230831-0002/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/fs/smb/server?id=2b9b8f3b68edb3d67d79962f02e26dbb5ae3808d
