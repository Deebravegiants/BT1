# [C] CVE-2023-38431

## Summary
Severity: Critical
Advisory: CVE-2023-38431
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2023-38431
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.8. fs/smb/server/connection.c in ksmbd does not validate the relationship between the NetBIOS header's length field and the SMB header sizes, via pdu_size in ksmbd_conn_handler_loop, leading to an out-of-bounds read.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.8
- https://security.netapp.com/advisory/ntap-20230824-0011/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/fs/smb/server?id=368ba06881c395f1c9a7ba22203cf8d78b4addc0
