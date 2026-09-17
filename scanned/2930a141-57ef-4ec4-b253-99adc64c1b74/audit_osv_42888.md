# [H] dm thin metadata: fix metadata snapshot consistency on commit failure

## Summary
Severity: High
Advisory: CVE-2026-72108
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72108
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm thin metadata: fix metadata snapshot consistency on commit failure

__reserve_metadata_snap() and __release_metadata_snap() modify the
superblock's held_root directly in the block_manager's buffer. If the
subsequent metadata commit fails, the held_root gets flushed to disk
through the abort_transaction path, resulting in inconsistent metadata.

Reproducer 1: __reserve_metadata_snap()

1. Create a 2 MiB metadata device and make the region after the 14th
   block inaccessible, to trigger metadata commit failure in the
   subsequent reserve_metadata_snap operation. The 14th block will be
   the shadow destination for the index block.

dmsetup create tmeta --table "0 112 linear /dev/sdc 0
112 3984 error"

2. Create a 16 MiB thin-pool

dmsetup create tdata --table "0 32768 zero"
dd if=/dev/zero of=/dev/mapper/tmeta bs=4k count=1
dmsetup create tpool --table "0 32768 thin-pool /dev/mapper/tmeta \
/dev/mapper/tdata 128 0 1 skip_block_zeroing"

3. Take a metadata snapshot to trigger metadata commit failure and
   transaction abort. However, the held_root is written to disk,
   breaking metadata consistency.

dmsetup message tpool 0 "reserve_metadata_snap"

thin_check v1.2.2 result:

Bad reference count for metadata block 6.  Expected 2, but space map contains 1.
Bad reference count for metadata block 7.  Expected 2, but space map contains 1.
Bad reference count for metadata block 13.  Expected 1, but space map contains 0.

Reproducer 2: __release_metadata_snap()

1. Create a 2 MiB metadata device and make the region after the 16th
   block inaccessible, to trigger metadata commit failure in the
   subsequent release_metadata_snap operation. The 16th block will be
   the shadow destination for the index block.

dmsetup create tmeta --table "0 128 linear /dev/sdc 0
128 3968 error"

2. Create a 16 MiB thin-pool

dmsetup create tdata --table "0 32768 zero"
dd if=/dev/zero of=/dev/mapper/tmeta bs=4k count=1
dmsetup create tpool --table "0 32768 thin-pool /dev/mapper/tmeta \
/dev/mapper/tdata 128 0 1 skip_block_zeroing"

3. Reserve then release the metadata snapshot, to trigger metadata
   commit failure and transaction abort. The held_root gets removed
   from the on-disk superblock, causing inconsistent metadata.

dmsetup message tpool 0 "reserve_metadata_snap"
dmsetup message tpool 0 "release_metadata_snap"

thin_check v1.2.2 result:

Bad reference count for metadata block 6.  Expected 1, but space map contains 2.
Bad reference count for metadata block 7.  Expected 1, but space map contains 2.
1 metadata blocks have leaked.

Fix by deferring the held_root update to commit time.

Additionally, move the existing-snapshot check in __reserve_metadata_snap
before the shadow operation to avoid unnecessary work. In
__release_metadata_snap, clear pmd->held_root before btree deletion so
partial failure leaks blocks rather than leaving a stale reference, and
unlock the snapshot block before decrementing its refcount.

## References
- https://git.kernel.org/stable/c/3dc9ae1029320d77472c44965e572f176949cd63
- https://git.kernel.org/stable/c/4af993468193cf4cd32ba5748786e7801945f7d2
- https://git.kernel.org/stable/c/5bcd4d3058ebaf46ad2e163829d87dd4870c7a45
- https://git.kernel.org/stable/c/5efb1a7734ed4035fa4fdc3716bdb84621f27cf6
- https://git.kernel.org/stable/c/7f76245960a332f39b08cc556e675d1765dc5bbb
- https://git.kernel.org/stable/c/9f1a0d27586ceab055e6b050e3731ce3c6b2c4f0
- https://git.kernel.org/stable/c/abf2fae92cbe68945028987d498cc72f8f0e23a8
- https://git.kernel.org/stable/c/b5f9a31c51cbb374a1713c3494f8660ab070f035
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72108.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72108
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
