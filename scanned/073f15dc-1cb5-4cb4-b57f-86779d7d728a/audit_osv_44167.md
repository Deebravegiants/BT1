# [H] xfs: bounds-check buffer log item's dirty bitmap

## Summary
Severity: High
Advisory: CVE-2026-80536
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80536
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.106, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfs: bounds-check buffer log item's dirty bitmap

xlog_recover_do_reg_buffer() replays each dirty region described by a
buffer log item's bitmap into the buffer read for that item:

	memcpy(xfs_buf_offset(bp, (uint)bit << XFS_BLF_SHIFT),
		item->ri_buf[i].iov_base,
		nbits << XFS_BLF_SHIFT);

The destination offset (bit/nbits, from the logged dirty bitmap) and the
buffer size (from the logged blf_len) are both attacker-controlled and
otherwise unrelated, yet the only thing bounding the copy is an ASSERT(),
which compiles away on production kernels. A crafted image logging a
small blf_len together with a bitmap bit past the end of that buffer
drives the memcpy() past the buffer's allocation, corrupting adjacent
kernel heap during mount-time log recovery. This is reachable by anyone
who can get a crafted image mounted -- the malicious-filesystem threat
model XFS already guards against elsewhere.

Turn the ASSERT() into a real XFS_IS_CORRUPT() check that aborts recovery
of the buffer with -EFSCORRUPTED, consistent with the validate-and-fail
idiom already used in xlog_recover_do_inode_buffer() and
xfs_dquot_item_recover.c. xlog_recover_do_reg_buffer() therefore becomes
STATIC int and its three callers propagate the error.

Found and confirmed with KASAN on a CONFIG_XFS_DEBUG=n build: the crafted
image trips a slab-out-of-bounds write before this change and fails
recovery cleanly with -EFSCORRUPTED after it.

## References
- https://git.kernel.org/stable/c/7e32d4eebae6ca24f8a673c107fd7eca1f47afc2
- https://git.kernel.org/stable/c/813f8136a2ce1fee266d02a7df73db6e8a541604
- https://git.kernel.org/stable/c/acb4e26295e7f0e685815a3fd3d70bd8329cefa1
- https://git.kernel.org/stable/c/b7528b42813f02724a78fce1da24d69d1bfc4d38
- https://git.kernel.org/stable/c/edaf5b6bd625356893da20d69a259b34a9de2694
- https://git.kernel.org/stable/c/f3859c35a4fbc1c1c58431f684f808e43696891d
- https://git.kernel.org/stable/c/f7b5fa83e2c192be922121b764415fa8c7549ea1
- https://git.kernel.org/stable/c/f8288214459ead7e87d26e5822f62c14a4f2ed6b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80536.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80536
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
