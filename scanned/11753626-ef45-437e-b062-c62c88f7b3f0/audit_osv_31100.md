# [H] Revert "libfs: fix infinite directory reads for offset dir"

## Summary
Severity: High
Advisory: CVE-2024-57952
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2024-57952
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.12, >=6.13.0 <6.13.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "libfs: fix infinite directory reads for offset dir"

The current directory offset allocator (based on mtree_alloc_cyclic)
stores the next offset value to return in octx->next_offset. This
mechanism typically returns values that increase monotonically over
time. Eventually, though, the newly allocated offset value wraps
back to a low number (say, 2) which is smaller than other already-
allocated offset values.

Yu Kuai <yukuai3@huawei.com> reports that, after commit 64a7ce76fb90
("libfs: fix infinite directory reads for offset dir"), if a
directory's offset allocator wraps, existing entries are no longer
visible via readdir/getdents because offset_readdir() stops listing
entries once an entry's offset is larger than octx->next_offset.
These entries vanish persistently -- they can be looked up, but will
never again appear in readdir(3) output.

The reason for this is that the commit treats directory offsets as
monotonically increasing integer values rather than opaque cookies,
and introduces this comparison:

	if (dentry2offset(dentry) >= last_index) {

On 64-bit platforms, the directory offset value upper bound is
2^63 - 1. Directory offsets will monotonically increase for millions
of years without wrapping.

On 32-bit platforms, however, LONG_MAX is 2^31 - 1. The allocator
can wrap after only a few weeks (at worst).

Revert commit 64a7ce76fb90 ("libfs: fix infinite directory reads for
offset dir") to prepare for a fix that can work properly on 32-bit
systems and might apply to recent LTS kernels where shmem employs
the simple_offset mechanism.

## References
- https://git.kernel.org/stable/c/3f250b82040a72b0059ae00855a74d8570ad2147
- https://git.kernel.org/stable/c/9e9e710f68bac49bd9b587823c077d06363440e0
- https://git.kernel.org/stable/c/b662d858131da9a8a14e68661656989b14dbf113
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57952.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57952
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
