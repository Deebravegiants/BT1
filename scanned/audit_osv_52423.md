# [M] CVE-2021-47433

## Summary
Severity: Medium
Advisory: CVE-2021-47433
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47433
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix abort logic in btrfs_replace_file_extents

Error injection testing uncovered a case where we'd end up with a
corrupt file system with a missing extent in the middle of a file.  This
occurs because the if statement to decide if we should abort is wrong.

The only way we would abort in this case is if we got a ret !=
-EOPNOTSUPP and we called from the file clone code.  However the
prealloc code uses this path too.  Instead we need to abort if there is
an error, and the only error we _don't_ abort on is -EOPNOTSUPP and only
if we came from the clone file code.

## References
- https://git.kernel.org/stable/c/0e309e1152fc34ef75991d9d69b165dbf75bf26c
- https://git.kernel.org/stable/c/0e32a2b85c7d92ece86c17dfef390c5ed79c6378
- https://git.kernel.org/stable/c/4afb912f439c4bc4e6a4f3e7547f2e69e354108f
