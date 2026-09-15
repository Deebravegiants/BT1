# [H] md/md-bitmap: fix incorrect usage for sb_index

## Summary
Severity: High
Advisory: CVE-2024-35787
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35787
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/md-bitmap: fix incorrect usage for sb_index

Commit d7038f951828 ("md-bitmap: don't use ->index for pages backing the
bitmap file") removed page->index from bitmap code, but left wrong code
logic for clustered-md. current code never set slot offset for cluster
nodes, will sometimes cause crash in clustered env.

Call trace (partly):
 md_bitmap_file_set_bit+0x110/0x1d8 [md_mod]
 md_bitmap_startwrite+0x13c/0x240 [md_mod]
 raid1_make_request+0x6b0/0x1c08 [raid1]
 md_handle_request+0x1dc/0x368 [md_mod]
 md_submit_bio+0x80/0xf8 [md_mod]
 __submit_bio+0x178/0x300
 submit_bio_noacct_nocheck+0x11c/0x338
 submit_bio_noacct+0x134/0x614
 submit_bio+0x28/0xdc
 submit_bh_wbc+0x130/0x1cc
 submit_bh+0x1c/0x28

## References
- https://git.kernel.org/stable/c/55e55eb65fd5e09faf5a0e49ffcdd37905aaf4da
- https://git.kernel.org/stable/c/5a95815b17428ce2f56ec18da5e0d1b2a1a15240
- https://git.kernel.org/stable/c/736ad6c577a367834118f57417038d45bb5e0a31
- https://git.kernel.org/stable/c/ecbd8ebb51bf7e4939d83b9e6022a55cac44ef06
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35787.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35787
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
