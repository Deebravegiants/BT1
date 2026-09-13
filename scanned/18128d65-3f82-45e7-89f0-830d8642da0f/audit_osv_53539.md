# [H] CVE-2022-48423

## Summary
Severity: High
Advisory: CVE-2022-48423
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-19
Source: https://osv.dev/vulnerability/CVE-2022-48423
Type: osv

## Details
In the Linux kernel before 6.1.3, fs/ntfs3/record.c does not validate resident attribute names. An out-of-bounds write may occur.

## References
- https://security.netapp.com/advisory/ntap-20230505-0003/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=54e45702b648b7c0000e90b3e9b890e367e16ea8
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.3
