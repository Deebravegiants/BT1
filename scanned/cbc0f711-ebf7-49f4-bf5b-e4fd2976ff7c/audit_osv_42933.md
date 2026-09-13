# [C] ntfs: make system files immutable to prevent corruption

## Summary
Severity: Critical
Advisory: CVE-2026-72186
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72186
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: make system files immutable to prevent corruption

When a system file such as $Bitmap is exposed via show_sys_files and
written from userspace, the volume is corrupted and, because the cluster
allocator scans $Bitmap through the same inode's page cache, a write to
$Bitmap also deadlocks writeback against the folio it already holds locked.

These files are maintained by the driver itself and have no valid reason
to be written through the file interface. Mark base metadata files
(mft_no < FILE_first_user) as immutable during inode read so the VFS
rejects write, mmap, truncate and unlink with -EPERM. Directories are
skipped so the root and $Extend remain usable. Internal metadata updates
do not go through the VFS write path and are unaffected.

## References
- https://git.kernel.org/stable/c/8f313e92522ac41d273ea137db13ea8a8df2beed
- https://git.kernel.org/stable/c/f72df3a4c33b64de3418ec74d1ad4f028e09d161
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72186.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72186
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
