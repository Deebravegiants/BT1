# [H] CVE-2022-48424

## Summary
Severity: High
Advisory: CVE-2022-48424
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-19
Source: https://osv.dev/vulnerability/CVE-2022-48424
Type: osv

## Details
In the Linux kernel before 6.1.3, fs/ntfs3/inode.c does not validate the attribute name offset. An unhandled page fault may occur.

## References
- https://security.netapp.com/advisory/ntap-20230505-0002/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.3
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4f1dc7d9756e66f3f876839ea174df2e656b7f79
