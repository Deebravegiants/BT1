# [H] minix: avoid overflow in bitmap block count calculation

## Summary
Severity: High
Advisory: CVE-2026-72369
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72369
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

minix: avoid overflow in bitmap block count calculation

minix_check_superblock() uses minix_blocks_needed() to verify that the
on-disk imap and zmap block counts are large enough for the advertised
inode and zone counts.

The helper currently performs DIV_ROUND_UP() in unsigned int arithmetic.
A Minix v3 image can set s_ninodes or s_zones near UINT_MAX so the
addition inside DIV_ROUND_UP() wraps to zero. That makes a zero imap/zmap
block count look valid, after which minix_fill_super() can dereference
s_imap[0] or s_zmap[0] even though no bitmap buffers were allocated.

Impact: mounting a crafted Minix v3 image whose s_ninodes or s_zones is
near UINT_MAX makes minix_check_superblock() accept a zero bitmap-block
count and minix_fill_super() dereference s_imap[0]/s_zmap[0], panicking
the kernel.

The divisor is the bitmap capacity in bits, blocksize * 8, which is
always a power of two: minix_fill_super() obtains the block size through
sb_set_blocksize(), and blk_validate_block_size() rejects any size that
is not a power of two. Use DIV_ROUND_UP_POW2(), which divides before
adding the round-up term and so cannot overflow for a power-of-two
divisor.

## References
- https://git.kernel.org/stable/c/8a29e60e2176b02e04f8737c8b32b696230eb0c5
- https://git.kernel.org/stable/c/959c95340a9e19cd333b4c18935fdeecbb2f319d
- https://git.kernel.org/stable/c/a11ebaab50d27d6c4c78506f84ff36452e0b901d
- https://git.kernel.org/stable/c/abe3536a4bedcc43de80b6d4d7e3d57e9ba382a5
- https://git.kernel.org/stable/c/fb3e566cafc38fe3ba35e6843a2d529a3748870c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72369.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72369
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
