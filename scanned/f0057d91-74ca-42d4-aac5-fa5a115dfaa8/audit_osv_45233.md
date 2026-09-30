# [M] Libarchive through 3.6.2 can cause directories to have world-writable permissions

## Summary
Severity: Medium
Advisory: JLSEC-2025-238
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-238
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.7.4+0

## Details
Libarchive through 3.6.2 can cause directories to have world-writable permissions. The umask() call inside `archive_write_disk_posix.c` changes the umask of the whole process for a very short period of time; a race condition with another thread can lead to a permanent umask 0 setting. Such a race condition could lead to implicit directory creation with permissions 0777 (without the sticky bit), which means that any low-privileged local user can delete and rename files inside those directories.

## References
- https://github.com/libarchive/libarchive/issues/1876
- https://groups.google.com/g/libarchive-announce
