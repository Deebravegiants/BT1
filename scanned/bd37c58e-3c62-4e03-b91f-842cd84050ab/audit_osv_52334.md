# [M] CVE-2021-47340

## Summary
Severity: Medium
Advisory: CVE-2021-47340
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47340
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: fix GPF in diFree

Avoid passing inode with
JFS_SBI(inode->i_sb)->ipimap == NULL to
diFree()[1]. GFP will appear:

	struct inode *ipimap = JFS_SBI(ip->i_sb)->ipimap;
	struct inomap *imap = JFS_IP(ipimap)->i_imap;

JFS_IP() will return invalid pointer when ipimap == NULL

Call Trace:
 diFree+0x13d/0x2dc0 fs/jfs/jfs_imap.c:853 [1]
 jfs_evict_inode+0x2c9/0x370 fs/jfs/inode.c:154
 evict+0x2ed/0x750 fs/inode.c:578
 iput_final fs/inode.c:1654 [inline]
 iput.part.0+0x3fe/0x820 fs/inode.c:1680
 iput+0x58/0x70 fs/inode.c:1670

## References
- https://git.kernel.org/stable/c/9d574f985fe33efd6911f4d752de6f485a1ea732
- https://git.kernel.org/stable/c/3bb27e27240289b47d3466f647a55c567adbdc3a
- https://git.kernel.org/stable/c/42f102ea1943ecb10a0756bf75424de5d1d5beed
- https://git.kernel.org/stable/c/8018936950360f1c503bb385e158cfc5e4945d18
- https://git.kernel.org/stable/c/a21e5cb1a64c904f1f0ef7b2d386fc7d2b1d2ce2
- https://git.kernel.org/stable/c/aff8d95b69051d0cf4acc3d91f22299fdbb9dfb3
- https://git.kernel.org/stable/c/49def1b0644892e3b113673c13d650c3060b43bc
- https://git.kernel.org/stable/c/745c9a59422c63f661f4374ed5181740db4130a1
- https://git.kernel.org/stable/c/7bde24bde490f3139eee147efc6d60d6040fe975
