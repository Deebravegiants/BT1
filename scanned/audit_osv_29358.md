# [H] nilfs2: add missing check for inode numbers on directory entries

## Summary
Severity: High
Advisory: CVE-2024-42104
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42104
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.98, >=6.2.0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: add missing check for inode numbers on directory entries

Syzbot reported that mounting and unmounting a specific pattern of
corrupted nilfs2 filesystem images causes a use-after-free of metadata
file inodes, which triggers a kernel bug in lru_add_fn().

As Jan Kara pointed out, this is because the link count of a metadata file
gets corrupted to 0, and nilfs_evict_inode(), which is called from iput(),
tries to delete that inode (ifile inode in this case).

The inconsistency occurs because directories containing the inode numbers
of these metadata files that should not be visible in the namespace are
read without checking.

Fix this issue by treating the inode numbers of these internal files as
errors in the sanity check helper when reading directory folios/pages.

Also thanks to Hillf Danton and Matthew Wilcox for their initial mm-layer
analysis.

## References
- https://git.kernel.org/stable/c/07c176e7acc5579c133bb923ab21316d192d0a95
- https://git.kernel.org/stable/c/1b7d549ed2c1fa202c751b69423a0d3a6bd5a180
- https://git.kernel.org/stable/c/265fff1a01cdc083aeaf0d934c929db5cc64aebf
- https://git.kernel.org/stable/c/2f2fa9cf7c3537958a82fbe8c8595a5eb0861ad7
- https://git.kernel.org/stable/c/3ab40870edb883b9633dc5cd55f5a2a11afa618d
- https://git.kernel.org/stable/c/b11e8fb93ea5eefb2e4e719497ea177a58ff6131
- https://git.kernel.org/stable/c/bb76c6c274683c8570ad788f79d4b875bde0e458
- https://git.kernel.org/stable/c/c33c2b0d92aa1c2262d999b2598ad6fbd53bd479
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42104.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42104
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
