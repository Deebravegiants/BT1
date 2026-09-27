# [H] f2fs: validate compress cache inode only when enabled

## Summary
Severity: High
Advisory: CVE-2026-63817
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63817
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.212, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: validate compress cache inode only when enabled

F2FS_COMPRESS_INO() uses NM_I(sbi)->max_nid as the synthetic inode
number for the compressed page cache inode. That inode only exists when
the compress_cache mount option is enabled.

When compress_cache is disabled, max_nid is outside the valid inode
range. A corrupted directory entry that points to ino == max_nid should
therefore be rejected by f2fs_check_nid_range(). However, is_meta_ino()
currently treats F2FS_COMPRESS_INO() as a meta inode unconditionally,
so f2fs_iget() bypasses do_read_inode() and its nid range check, and
instantiates a fake internal inode instead.

Gate the compressed cache inode case on COMPRESS_CACHE, matching
f2fs_init_compress_inode(). With compress_cache disabled, ino ==
max_nid now follows the normal inode path and is rejected as an
out-of-range nid.

## References
- https://git.kernel.org/stable/c/0969926d987bbde9a1aa49da317582ba37095805
- https://git.kernel.org/stable/c/13e4b59d3a9413f66f116fa6c4828519b960a5ea
- https://git.kernel.org/stable/c/16161444c30d8dff9428abbae42b72ce4e32a932
- https://git.kernel.org/stable/c/29115b8c9172d34e67ab26cc4f6c209b7a236d7a
- https://git.kernel.org/stable/c/5073c66a96a9c23c0c2533ed4ed06e42f9021208
- https://git.kernel.org/stable/c/77f216ff9ce5cde8eed9f6d12707e906dffdc9f7
- https://git.kernel.org/stable/c/fcc051d377a9701a452e7663a1a8223c26225df9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63817.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63817
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
