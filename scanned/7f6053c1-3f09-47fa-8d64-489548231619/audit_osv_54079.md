# [C] CVE-2023-38428

## Summary
Severity: Critical
Advisory: CVE-2023-38428
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2023-38428
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.4. fs/ksmbd/smb2pdu.c in ksmbd does not properly check the UserName value because it does not consider the address of security buffer, leading to an out-of-bounds read.

## References
- https://security.netapp.com/advisory/ntap-20230831-0001/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/fs/ksmbd?id=f0a96d1aafd8964e1f9955c830a3e5cb3c60a90f
