# [C] CVE-2023-38429

## Summary
Severity: Critical
Advisory: CVE-2023-38429
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2023-38429
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.4. fs/ksmbd/connection.c in ksmbd has an off-by-one error in memory allocation (because of ksmbd_smb2_check_message) that may lead to out-of-bounds access.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.4
- https://security.netapp.com/advisory/ntap-20250103-0009/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/fs/ksmbd?id=443d61d1fa9faa60ef925513d83742902390100f
