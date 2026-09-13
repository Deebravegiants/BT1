# [M] CVE-2021-47113

## Summary
Severity: Medium
Advisory: CVE-2021-47113
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47113
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: abort in rename_exchange if we fail to insert the second ref

Error injection stress uncovered a problem where we'd leave a dangling
inode ref if we failed during a rename_exchange.  This happens because
we insert the inode ref for one side of the rename, and then for the
other side.  If this second inode ref insert fails we'll leave the first
one dangling and leave a corrupt file system behind.  Fix this by
aborting if we did the insert for the first inode ref.

## References
- https://git.kernel.org/stable/c/dc09ef3562726cd520c8338c1640872a60187af5
- https://git.kernel.org/stable/c/ff8de2cec65a8c8521faade12a31b39c80e49f5b
- https://git.kernel.org/stable/c/0df50d47d17401f9f140dfbe752a65e5d72f9932
