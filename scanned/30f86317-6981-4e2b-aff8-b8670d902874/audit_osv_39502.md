# [H] gfs2: Fix use-after-free in iomap inline data write path

## Summary
Severity: High
Advisory: CVE-2026-45984
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45984
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: Fix use-after-free in iomap inline data write path

The inline data buffer head (dibh) is being released prematurely in
gfs2_iomap_begin() via release_metapath() while iomap->inline_data
still points to dibh->b_data. This causes a use-after-free when
iomap_write_end_inline() later attempts to write to the inline data
area.

The bug sequence:
1. gfs2_iomap_begin() calls gfs2_meta_inode_buffer() to read inode
   metadata into dibh
2. Sets iomap->inline_data = dibh->b_data + sizeof(struct gfs2_dinode)
3. Calls release_metapath() which calls brelse(dibh), dropping refcount
   to 0
4. kswapd reclaims the page (~39ms later in the syzbot report)
5. iomap_write_end_inline() tries to memcpy() to iomap->inline_data
6. KASAN detects use-after-free write to freed memory

Fix by storing dibh in iomap->private and incrementing its refcount
with get_bh() in gfs2_iomap_begin(). The buffer is then properly
released in gfs2_iomap_end() after the inline write completes,
ensuring the page stays alive for the entire iomap operation.

Note: A C reproducer is not available for this issue. The fix is based
on analysis of the KASAN report and code review showing the buffer head
is freed before use.

[agruenba: Take buffer head reference in gfs2_iomap_begin() to avoid
leaks in gfs2_iomap_get() and gfs2_iomap_alloc().]

## References
- https://git.kernel.org/stable/c/1403989d1b502f4a2c0d0b42ccf1c25748442eff
- https://git.kernel.org/stable/c/1cae1bafdf9caa9b462b19af06b1a06902e4e142
- https://git.kernel.org/stable/c/6d76febba07c40bcf358f63216d36ea68cf1c215
- https://git.kernel.org/stable/c/764c3c84b5683e608f43735c803a5f415046686c
- https://git.kernel.org/stable/c/815ddd27c0c7171a99fe802fdb19098ddef8b19d
- https://git.kernel.org/stable/c/87d4954b5c59735a99ea98cb208d47130f6dce7d
- https://git.kernel.org/stable/c/d87268326b277af3665237ac76a73dd9fa8e21b4
- https://git.kernel.org/stable/c/faddeb848305e79db89ee0479bb0e33380656321
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45984.json
- https://access.redhat.com/errata/RHSA-2026:27789
- https://access.redhat.com/errata/RHSA-2026:33743
- https://access.redhat.com/errata/RHSA-2026:35894
- https://access.redhat.com/errata/RHSA-2026:36049
- https://access.redhat.com/errata/RHSA-2026:36767
- https://access.redhat.com/errata/RHSA-2026:38902
- https://access.redhat.com/errata/RHSA-2026:51603
- https://access.redhat.com/errata/RHSA-2026:51604
- https://access.redhat.com/errata/RHSA-2026:55444
- https://access.redhat.com/errata/RHSA-2026:59142
- https://access.redhat.com/errata/RHSA-2026:59143
