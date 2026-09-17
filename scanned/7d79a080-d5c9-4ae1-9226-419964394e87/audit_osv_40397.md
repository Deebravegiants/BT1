# [H] fs/omfs: reject s_sys_blocksize smaller than OMFS_DIR_START

## Summary
Severity: High
Advisory: CVE-2026-53130
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53130
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/omfs: reject s_sys_blocksize smaller than OMFS_DIR_START

omfs_fill_super() rejects oversized s_sys_blocksize values (> PAGE_SIZE),
but it does not reject values smaller than OMFS_DIR_START (0x1b8 = 440).

Later, omfs_make_empty() uses

    sbi->s_sys_blocksize - OMFS_DIR_START

as the length argument to memset().  Since s_sys_blocksize is u32,
a crafted filesystem image with s_sys_blocksize < OMFS_DIR_START causes
an unsigned underflow there, wrapping to a value near 2^32.  That drives
a ~4 GiB memset() from bh->b_data + OMFS_DIR_START and overwrites kernel
memory far beyond the backing block buffer.

Add the corresponding lower-bound check alongside the existing upper-bound
check in omfs_fill_super(), so that malformed images are rejected during
superblock validation before any filesystem data is processed.

## References
- https://git.kernel.org/stable/c/0621c385fda1376e967f37ccd534c26c3e511d14
- https://git.kernel.org/stable/c/131ea3e57fc22936ed0e2c8330f2e36106172f51
- https://git.kernel.org/stable/c/5822a05a841a10794ad818620dd2af490b0705d3
- https://git.kernel.org/stable/c/6561afc38398e3518a29c5eebb975c30468f98a6
- https://git.kernel.org/stable/c/754ff1bea3819a90c6f33cccfc1a299ef7609f07
- https://git.kernel.org/stable/c/79f84af38c9fef9deb0e02c79eb969b5541c2644
- https://git.kernel.org/stable/c/817f16ed62bc58a168417bfb5e859c2a370bab03
- https://git.kernel.org/stable/c/fbc72f5c645155dc2ed3573243ed20f9913e3a54
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53130.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53130
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
