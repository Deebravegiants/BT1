# [H] CVE-2019-15918

## Summary
Severity: High
Advisory: CVE-2019-15918
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-15918
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.10. SMB2_negotiate in fs/cifs/smb2pdu.c has an out-of-bounds read because data structures are incompletely updated after a change from smb30 to smb21.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.10
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://usn.ubuntu.com/4162-1/
- https://usn.ubuntu.com/4162-2/
- https://github.com/torvalds/linux/commit/b57a55e2200ede754e4dc9cce4ba9402544b9365
