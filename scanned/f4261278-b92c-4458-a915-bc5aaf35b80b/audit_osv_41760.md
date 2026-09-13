# [H] f2fs: bound i_inline_xattr_size for non-inline-xattr inodes

## Summary
Severity: High
Advisory: CVE-2026-63815
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63815
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: bound i_inline_xattr_size for non-inline-xattr inodes

When the flexible_inline_xattr feature is enabled, do_read_inode() loads
the on-disk i_inline_xattr_size unconditionally:

	if (f2fs_sb_has_flexible_inline_xattr(sbi))
		fi->i_inline_xattr_size = le16_to_cpu(ri->i_inline_xattr_size);

but sanity_check_inode() only range-checks it when the inode also has the
FI_INLINE_XATTR flag set.  An inode that carries an inline dentry or inline
data but not FI_INLINE_XATTR -- the normal layout for an inline
directory -- therefore keeps a fully attacker-controlled
i_inline_xattr_size from a crafted image.

get_inline_xattr_addrs() returns that value with no flag gating, so it
feeds the inode geometry:

	MAX_INLINE_DATA()  = 4 * (CUR_ADDRS_PER_INODE - i_inline_xattr_size - 1)
	NR_INLINE_DENTRY() = MAX_INLINE_DATA() * BITS_PER_BYTE / (...)
	addrs_per_page()   = CUR_ADDRS_PER_INODE - i_inline_xattr_size

A large i_inline_xattr_size drives MAX_INLINE_DATA() and NR_INLINE_DENTRY()
negative, so make_dentry_ptr_inline() sets d->max (int) to a negative
value.  The inline directory walk then compares an unsigned long bit_pos
against that negative d->max, which is promoted to a huge unsigned bound,
and reads far past the inline area:

	while (bit_pos < d->max)		/* fs/f2fs/dir.c */
		... test_bit_le(bit_pos, d->bitmap) / d->dentry[bit_pos] ...

Mounting a crafted image and reading such a directory triggers an
out-of-bounds read in f2fs_fill_dentries(); the same underflow also
corrupts ADDRS_PER_INODE for regular files.

Validate i_inline_xattr_size against MAX_INLINE_XATTR_SIZE whenever the
flexible_inline_xattr feature is enabled -- i.e. whenever the value is
loaded from disk and consumed -- and keep the lower MIN_INLINE_XATTR_SIZE
bound gated on inodes that actually carry an inline xattr, so legitimate
inodes with i_inline_xattr_size == 0 are still accepted.

## References
- https://git.kernel.org/stable/c/16bc237ce3c483b75575abea53cfb639745311ed
- https://git.kernel.org/stable/c/2a9f9791653ba5ed3fb45bbffa8d63a7cd5cf706
- https://git.kernel.org/stable/c/378acf3cf19b6af6cba55e8dd1154c4e1504bae8
- https://git.kernel.org/stable/c/3c8d6b4093aea40a20596f452289e7c22d84e6d5
- https://git.kernel.org/stable/c/4ce2d52f680c1d8bfdad7cce05b815ea7ca9790d
- https://git.kernel.org/stable/c/76e1a05cf6d4051931d7fa4ead51a05786a62918
- https://git.kernel.org/stable/c/a08ee30dcbeff6b97df75c38c2589603ddde53a6
- https://git.kernel.org/stable/c/c3e05522daae4e7348a1ea81eeb321d25aa0fd3b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63815.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63815
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
