# [M] btrfs: add handling for RAID1C23/DUP to btrfs_reduce_alloc_profile

## Summary
Severity: Medium
Advisory: CVE-2023-53243
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53243
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: add handling for RAID1C23/DUP to btrfs_reduce_alloc_profile

Callers of `btrfs_reduce_alloc_profile` expect it to return exactly
one allocation profile flag, and failing to do so may ultimately
result in a WARN_ON and remount-ro when allocating new blocks, like
the below transaction abort on 6.1.

`btrfs_reduce_alloc_profile` has two ways of determining the profile,
first it checks if a conversion balance is currently running and
uses the profile we're converting to. If no balance is currently
running, it returns the max-redundancy profile which at least one
block in the selected block group has.

This works by simply checking each known allocation profile bit in
redundancy order. However, `btrfs_reduce_alloc_profile` has not been
updated as new flags have been added - first with the `DUP` profile
and later with the RAID1C34 profiles.

Because of the way it checks, if we have blocks with different
profiles and at least one is known, that profile will be selected.
However, if none are known we may return a flag set with multiple
allocation profiles set.

This is currently only possible when a balance from one of the three
unhandled profiles to another of the unhandled profiles is canceled
after allocating at least one block using the new profile.

In that case, a transaction abort like the below will occur and the
filesystem will need to be mounted with -o skip_balance to get it
mounted rw again (but the balance cannot be resumed without a
similar abort).

  [770.648] ------------[ cut here ]------------
  [770.648] BTRFS: Transaction aborted (error -22)
  [770.648] WARNING: CPU: 43 PID: 1159593 at fs/btrfs/extent-tree.c:4122 find_free_extent+0x1d94/0x1e00 [btrfs]
  [770.648] CPU: 43 PID: 1159593 Comm: btrfs Tainted: G        W 6.1.0-0.deb11.7-powerpc64le #1  Debian 6.1.20-2~bpo11+1a~test
  [770.648] Hardware name: T2P9D01 REV 1.00 POWER9 0x4e1202 opal:skiboot-bc106a0 PowerNV
  [770.648] NIP:  c00800000f6784fc LR: c00800000f6784f8 CTR: c000000000d746c0
  [770.648] REGS: c000200089afe9a0 TRAP: 0700   Tainted: G        W (6.1.0-0.deb11.7-powerpc64le Debian 6.1.20-2~bpo11+1a~test)
  [770.648] MSR:  9000000002029033 <SF,HV,VEC,EE,ME,IR,DR,RI,LE>  CR: 28848282  XER: 20040000
  [770.648] CFAR: c000000000135110 IRQMASK: 0
	    GPR00: c00800000f6784f8 c000200089afec40 c00800000f7ea800 0000000000000026
	    GPR04: 00000001004820c2 c000200089afea00 c000200089afe9f8 0000000000000027
	    GPR08: c000200ffbfe7f98 c000000002127f90 ffffffffffffffd8 0000000026d6a6e8
	    GPR12: 0000000028848282 c000200fff7f3800 5deadbeef0000122 c00000002269d000
	    GPR16: c0002008c7797c40 c000200089afef17 0000000000000000 0000000000000000
	    GPR20: 0000000000000000 0000000000000001 c000200008bc5a98 0000000000000001
	    GPR24: 0000000000000000 c0000003c73088d0 c000200089afef17 c000000016d3a800
	    GPR28: c0000003c7308800 c00000002269d000 ffffffffffffffea 0000000000000001
  [770.648] NIP [c00800000f6784fc] find_free_extent+0x1d94/0x1e00 [btrfs]
  [770.648] LR [c00800000f6784f8] find_free_extent+0x1d90/0x1e00 [btrfs]
  [770.648] Call Trace:
  [770.648] [c000200089afec40] [c00800000f6784f8] find_free_extent+0x1d90/0x1e00 [btrfs] (unreliable)
  [770.648] [c000200089afed30] [c00800000f681398] btrfs_reserve_extent+0x1a0/0x2f0 [btrfs]
  [770.648] [c000200089afeea0] [c00800000f681bf0] btrfs_alloc_tree_block+0x108/0x670 [btrfs]
  [770.648] [c000200089afeff0] [c00800000f66bd68] __btrfs_cow_block+0x170/0x850 [btrfs]
  [770.648] [c000200089aff100] [c00800000f66c58c] btrfs_cow_block+0x144/0x288 [btrfs]
  [770.648] [c000200089aff1b0] [c00800000f67113c] btrfs_search_slot+0x6b4/0xcb0 [btrfs]
  [770.648] [c000200089aff2a0] [c00800000f679f60] lookup_inline_extent_backref+0x128/0x7c0 [btrfs]
  [770.648] [c000200089aff3b0] [c00800000f67b338] lookup_extent_backref+0x70/0x190 [btrfs]
  [770.648] [c000200089aff470] [c00800000f67b54c] __btrfs_free_extent+0xf4/0x1490 [btrfs]
  [770.648] [
---truncated---

## References
- https://git.kernel.org/stable/c/12b6d68498982a053a4a7e561a04387e57ca6f1a
- https://git.kernel.org/stable/c/160fe8f6fdb13da6111677be6263e5d65e875987
- https://git.kernel.org/stable/c/1b532748ba00bd2a1d9b09e0d5e81280582c7770
- https://git.kernel.org/stable/c/4fadf53fa95142f01f215012e97c384529759a72
- https://git.kernel.org/stable/c/a3fbd156bd2cd16e3c64e250ebce33eb9f2ef612
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53243.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53243
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
