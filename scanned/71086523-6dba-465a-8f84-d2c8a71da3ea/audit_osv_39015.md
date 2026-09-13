# [H] xfs: fix undersized l_iclog_roundoff values

## Summary
Severity: High
Advisory: CVE-2026-43365
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43365
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: fix undersized l_iclog_roundoff values

If the superblock doesn't list a log stripe unit, we set the incore log
roundoff value to 512.  This leads to corrupt logs and unmountable
filesystems in generic/617 on a disk with 4k physical sectors...

XFS (sda1): Mounting V5 Filesystem ff3121ca-26e6-4b77-b742-aaff9a449e1c
XFS (sda1): Torn write (CRC failure) detected at log block 0x318e. Truncating head block from 0x3197.
XFS (sda1): failed to locate log tail
XFS (sda1): log mount/recovery failed: error -74
XFS (sda1): log mount failed
XFS (sda1): Mounting V5 Filesystem ff3121ca-26e6-4b77-b742-aaff9a449e1c
XFS (sda1): Ending clean mount

...on the current xfsprogs for-next which has a broken mkfs.  xfs_info
shows this...

meta-data=/dev/sda1              isize=512    agcount=4, agsize=644992 blks
         =                       sectsz=4096  attr=2, projid32bit=1
         =                       crc=1        finobt=1, sparse=1, rmapbt=1
         =                       reflink=1    bigtime=1 inobtcount=1 nrext64=1
         =                       exchange=1   metadir=1
data     =                       bsize=4096   blocks=2579968, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0, ftype=1, parent=1
log      =internal log           bsize=4096   blocks=16384, version=2
         =                       sectsz=4096  sunit=0 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0
         =                       rgcount=0    rgsize=268435456 extents
         =                       zoned=0      start=0 reserved=0

...observe that the log section has sectsz=4096 sunit=0, which means
that the roundoff factor is 512, not 4096 as you'd expect.  We should
fix mkfs not to generate broken filesystems, but anyone can fuzz the
ondisk superblock so we should be more cautious.  I think the inadequate
logic predates commit a6a65fef5ef8d0, but that's clearly going to
require a different backport.

## References
- https://git.kernel.org/stable/c/2ecda4b83749c1fef0c9dea4fd5e8b513aba3e40
- https://git.kernel.org/stable/c/41e91dff2d3974730b5ee50daa8e27ec254cbf91
- https://git.kernel.org/stable/c/446a1f5bb64ba38adb93cb043ff0f7b85e8937ca
- https://git.kernel.org/stable/c/52a8a1ba883defbfe3200baa22cf4cd21985d51a
- https://git.kernel.org/stable/c/5afae524f83d6a18517298491a5624cb0eae5029
- https://git.kernel.org/stable/c/5e7148402dfc4a5b7894d8e97b15e5c2e70924aa
- https://git.kernel.org/stable/c/e88ce9f0536f3b2149afb70625cfc4bd74a4ac6d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43365.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43365
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
