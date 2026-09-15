# [H] jfs: jfs_dmap: Validate db_l2nbperpage while mounting

## Summary
Severity: High
Advisory: CVE-2023-53222
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53222
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.322, >=4.15.0 <4.19.291, >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: jfs_dmap: Validate db_l2nbperpage while mounting

In jfs_dmap.c at line 381, BLKTODMAP is used to get a logical block
number inside dbFree(). db_l2nbperpage, which is the log2 number of
blocks per page, is passed as an argument to BLKTODMAP which uses it
for shifting.

Syzbot reported a shift out-of-bounds crash because db_l2nbperpage is
too big. This happens because the large value is set without any
validation in dbMount() at line 181.

Thus, make sure that db_l2nbperpage is correct while mounting.

Max number of blocks per page = Page size / Min block size
=> log2(Max num_block per page) = log2(Page size / Min block size)
				= log2(Page size) - log2(Min block size)

=> Max db_l2nbperpage = L2PSIZE - L2MINBLOCKSIZE

## References
- https://git.kernel.org/stable/c/11509910c599cbd04585ec35a6d5e1a0053d84c1
- https://git.kernel.org/stable/c/2a03c4e683d33d17b667418eb717b13dda1fac6b
- https://git.kernel.org/stable/c/47b7eaae08e8b2f25bdf37bc14d21be090bcb20f
- https://git.kernel.org/stable/c/8c1efe3f74a7864461b0dff281c5562154b4aa8e
- https://git.kernel.org/stable/c/a4855aeb13e4ad1f23e16753b68212e180f7d848
- https://git.kernel.org/stable/c/c7feb54b113802d2aba98708769d3c33fb017254
- https://git.kernel.org/stable/c/de984faecddb900fa850af4df574a25b32bb93f5
- https://git.kernel.org/stable/c/ef5c205b6e6f8d1f18ef0b4a9832b1b5fa85f7f2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53222.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53222
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
