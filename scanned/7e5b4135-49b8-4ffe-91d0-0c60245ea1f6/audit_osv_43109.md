# [H] fs/ntfs3: prevent potential lcn remains uninitialized

## Summary
Severity: High
Advisory: CVE-2026-72471
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72471
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: prevent potential lcn remains uninitialized

The target VCN being sought was not found within runs[0], causing
run_lookup() to return false. This causes run_lookup_entry() to return
false, which in turn results in a len value of 0, and the new parameter
passed to attr_data_get_block() is NULL. Collectively, these factors
ultimately cause attr_data_get_block_locked() to exit prematurely without
initializing lcn, thereby triggering [1].

To prevent [1], the clen check within ni_seek_data_or_hole() has been
moved to occur before the lcn check.

[1]
BUG: KMSAN: uninit-value in ni_seek_data_or_hole+0x24f/0x5f0 fs/ntfs3/frecord.c:2862
 ni_seek_data_or_hole+0x24f/0x5f0 fs/ntfs3/frecord.c:2862
 ntfs_llseek+0x22a/0x4a0 fs/ntfs3/file.c:1530
 vfs_llseek fs/read_write.c:391 [inline]

## References
- https://git.kernel.org/stable/c/57ac2831c8e0f168090d38e3de758c6a59db44db
- https://git.kernel.org/stable/c/7ae7e98b71438c494532492cbf58fc0d7f7988bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72471.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72471
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
