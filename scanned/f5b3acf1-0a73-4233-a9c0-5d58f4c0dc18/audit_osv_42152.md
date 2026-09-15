# [H] xfs: resample the data fork mapping after cycling ILOCK

## Summary
Severity: High
Advisory: CVE-2026-64600
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-64600
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: resample the data fork mapping after cycling ILOCK

xfs_reflink_fill_{cow_hole,delalloc} are both presented with an inode,
a data fork mapping, and a cow fork mapping.  Unfortunately, these two
helpers cycle the ILOCK to grab a transaction, which means that the
mappings are stale as soon as we reacquire the ILOCK.  Currently we
refresh the cow fork mapping by re-calling xfs_find_trim_cow_extent, but
we don't refresh the data fork mapping beforehand, which means that the
xfs_bmap_trim_cow in that function queries the refcount btree about the
wrong physical blocks and returns an inaccurate value in *shared.

If *shared is now false, the directio write proceeds with a stale data
fork mapping.  Fix this by querying the data fork mapping if the
sequence counter changes across the ILOCK cycle.

## References
- http://www.openwall.com/lists/oss-security/2026/07/22/14
- http://www.openwall.com/lists/oss-security/2026/07/22/18
- http://www.openwall.com/lists/oss-security/2026/07/22/19
- http://www.openwall.com/lists/oss-security/2026/07/31/3
- http://www.openwall.com/lists/oss-security/2026/08/03/4
- http://www.openwall.com/lists/oss-security/2026/08/03/8
- https://git.kernel.org/stable/c/206c09b04dc5469c7ff14d8aceff2d47c88078d9
- https://git.kernel.org/stable/c/2f4acd0fcd862e22eab45690ec2c08c80b6ef2e7
- https://git.kernel.org/stable/c/44f891bc088958399eec27f7604928694aa35581
- https://git.kernel.org/stable/c/50f0012da1040f69a4e788cd9aed587c9a04983f
- https://git.kernel.org/stable/c/b8c9aa832b52680ee40d6cab0efb081f9a69df05
- https://git.kernel.org/stable/c/dc11be133efca5fe3a2fb02b016dee825cc12f18
- https://git.kernel.org/stable/c/e705d81a7193dd19e69b8e2bad4696d78a4ea075
- https://cdn2.qualys.com/advisory/2026/07/22/RefluXFS.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64600.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64600
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
