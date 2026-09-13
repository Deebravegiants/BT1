# [H] ext4: validate p_idx bounds in ext4_ext_correct_indexes

## Summary
Severity: High
Advisory: CVE-2026-31449
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31449
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: validate p_idx bounds in ext4_ext_correct_indexes

ext4_ext_correct_indexes() walks up the extent tree correcting
index entries when the first extent in a leaf is modified. Before
accessing path[k].p_idx->ei_block, there is no validation that
p_idx falls within the valid range of index entries for that
level.

If the on-disk extent header contains a corrupted or crafted
eh_entries value, p_idx can point past the end of the allocated
buffer, causing a slab-out-of-bounds read.

Fix this by validating path[k].p_idx against EXT_LAST_INDEX() at
both access sites: before the while loop and inside it. Return
-EFSCORRUPTED if the index pointer is out of range, consistent
with how other bounds violations are handled in the ext4 extent
tree code.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/01bf1e0b997d82c0e353b51ed74ef99698043c33
- https://git.kernel.org/stable/c/10242e640b36b91ad03d25f3dc77854bbdff8358
- https://git.kernel.org/stable/c/2acb5c12ebd860f30e4faf67e6cc8c44ddfe5fe8
- https://git.kernel.org/stable/c/39d6e2b67651614bac0dc6592fa9836321910067
- https://git.kernel.org/stable/c/407c944f217c17d4343148011acafebc604d55e1
- https://git.kernel.org/stable/c/4d08401aa13f1531216f1a7ae281ca4806e90a5c
- https://git.kernel.org/stable/c/93f2e975ed658ce09db4d4c2877ca2c06540df83
- https://git.kernel.org/stable/c/c5839b34704c9c2f47f079451bdbb22de0da1ed1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31449.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31449
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
