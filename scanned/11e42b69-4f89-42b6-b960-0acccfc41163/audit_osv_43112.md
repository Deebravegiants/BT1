# [C] fs/ntfs3: call _ntfs_bad_inode() when failing to rename

## Summary
Severity: Critical
Advisory: CVE-2026-72477
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72477
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: call _ntfs_bad_inode() when failing to rename

It is safe to call _ntfs_bad_inode on live inodes since:
  commit 519b078998ce ("fs/ntfs3: Exclude call make_bad_inode for live nodes.")

The WARN_ON was added when it wasn't safe by:
  commit d99208b91933 ("fs/ntfs3: cancle set bad inode after removing name fails")

Replace the WARN_ON with a call to _ntfs_bad_inode() to prevent further
operations on the inconsistent inode.

## References
- https://git.kernel.org/stable/c/e8ed78f40eecd0176fda71d673f6957c98e7ffbe
- https://git.kernel.org/stable/c/ff825bf0521f6da2f30878cbad18ab7b341bc31b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72477.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72477
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
