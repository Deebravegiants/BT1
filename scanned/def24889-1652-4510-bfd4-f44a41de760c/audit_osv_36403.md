# [H] apparmor: fix race between freeing data and fs accessing it

## Summary
Severity: High
Advisory: CVE-2026-23411
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-23411
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.18, >=6.19.0 <6.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: fix race between freeing data and fs accessing it

AppArmor was putting the reference to i_private data on its end after
removing the original entry from the file system. However the inode
can aand does live beyond that point and it is possible that some of
the fs call back functions will be invoked after the reference has
been put, which results in a race between freeing the data and
accessing it through the fs.

While the rawdata/loaddata is the most likely candidate to fail the
race, as it has the fewest references. If properly crafted it might be
possible to trigger a race for the other types stored in i_private.

Fix this by moving the put of i_private referenced data to the correct
place which is during inode eviction.

## References
- https://git.kernel.org/stable/c/13bc2772414d68e94e273dea013181a986948ddf
- https://git.kernel.org/stable/c/2a732ed26fbd048e7925d227af8cf9ea43fb5cc9
- https://git.kernel.org/stable/c/3ddb961d2929bbb3204a2bba21b5d8153cd3f7cc
- https://git.kernel.org/stable/c/667df93769c02ff581c77d2d8f162147e719c557
- https://git.kernel.org/stable/c/8e135b8aee5a06c52a4347a5a6d51223c6f36ba3
- https://git.kernel.org/stable/c/a92c5e5086a87d082696245a8607666da3d80554
- https://git.kernel.org/stable/c/ae10787d955fb255d381e0d5589451dd72c614b1
- https://git.kernel.org/stable/c/eecce026399917f6efa532c56bc7a3e9dd6ee68b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23411.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23411
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
