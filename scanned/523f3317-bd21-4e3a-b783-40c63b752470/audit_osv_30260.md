# [H] fsdax: dax_unshare_iter needs to copy entire blocks

## Summary
Severity: High
Advisory: CVE-2024-50250
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50250
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.116, >=6.2.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

fsdax: dax_unshare_iter needs to copy entire blocks

The code that copies data from srcmap to iomap in dax_unshare_iter is
very very broken, which bfoster's recent fsx changes have exposed.

If the pos and len passed to dax_file_unshare are not aligned to an
fsblock boundary, the iter pos and length in the _iter function will
reflect this unalignment.

dax_iomap_direct_access always returns a pointer to the start of the
kmapped fsdax page, even if its pos argument is in the middle of that
page.  This is catastrophic for data integrity when iter->pos is not
aligned to a page, because daddr/saddr do not point to the same byte in
the file as iter->pos.  Hence we corrupt user data by copying it to the
wrong place.

If iter->pos + iomap_length() in the _iter function not aligned to a
page, then we fail to copy a full block, and only partially populate the
destination block.  This is catastrophic for data confidentiality
because we expose stale pmem contents.

Fix both of these issues by aligning copy_pos/copy_len to a page
boundary (remember, this is fsdax so 1 fsblock == 1 base page) so that
we always copy full blocks.

We're not done yet -- there's no call to invalidate_inode_pages2_range,
so programs that have the file range mmap'd will continue accessing the
old memory mapping after the file metadata updates have completed.

Be careful with the return value -- if the unshare succeeds, we still
need to return the number of bytes that the iomap iter thinks we're
operating on.

## References
- https://git.kernel.org/stable/c/50793801fc7f6d08def48754fb0f0706b0cfc394
- https://git.kernel.org/stable/c/8e9c0f500b42216ef930f5c0d1703989a451913d
- https://git.kernel.org/stable/c/9bc18bb476e50e32e5d08f2734d63d63e0fa528c
- https://git.kernel.org/stable/c/bdbc96c23197d773a7d1bf03e4f11de593b0ff28
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50250.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50250
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
