# [C] CVE-2023-38427

## Summary
Severity: Critical
Advisory: CVE-2023-38427
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2023-38427
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.8. fs/smb/server/smb2pdu.c in ksmbd has an integer underflow and out-of-bounds read in deassemble_neg_contexts.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.8
- https://security.netapp.com/advisory/ntap-20230824-0011/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/fs/smb/server?id=f1a411873c85b642f13b01f21b534c2bab81fc1b
