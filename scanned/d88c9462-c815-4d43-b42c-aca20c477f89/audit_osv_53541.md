# [H] CVE-2022-48425

## Summary
Severity: High
Advisory: CVE-2022-48425
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-19
Source: https://osv.dev/vulnerability/CVE-2022-48425
Type: osv

## Details
In the Linux kernel through 6.2.7, fs/ntfs3/inode.c has an invalid kfree because it does not validate MFT flags before replaying logs.

## References
- https://security.netapp.com/advisory/ntap-20230413-0006/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=467333af2f7b95eeaa61a5b5369a80063cd971fd
- https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/fs/ntfs3?id=467333af2f7b95eeaa61a5b5369a80063cd971fd
