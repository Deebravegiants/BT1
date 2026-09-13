# [H] ext4: fix delayed allocation bug in ext4_clu_mapped for bigalloc + inline

## Summary
Severity: High
Advisory: CVE-2022-50286
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50286
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.271, >=4.20.0 <5.10.163, >=5.5.0 <5.15.87, >=5.11.0 <6.0.18, >=5.16.0 <6.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix delayed allocation bug in ext4_clu_mapped for bigalloc + inline

When converting files with inline data to extents, delayed allocations
made on a file system created with both the bigalloc and inline options
can result in invalid extent status cache content, incorrect reserved
cluster counts, kernel memory leaks, and potential kernel panics.

With bigalloc, the code that determines whether a block must be
delayed allocated searches the extent tree to see if that block maps
to a previously allocated cluster.  If not, the block is delayed
allocated, and otherwise, it isn't.  However, if the inline option is
also used, and if the file containing the block is marked as able to
store data inline, there isn't a valid extent tree associated with
the file.  The current code in ext4_clu_mapped() calls
ext4_find_extent() to search the non-existent tree for a previously
allocated cluster anyway, which typically finds nothing, as desired.
However, a side effect of the search can be to cache invalid content
from the non-existent tree (garbage) in the extent status tree,
including bogus entries in the pending reservation tree.

To fix this, avoid searching the extent tree when allocating blocks
for bigalloc + inline files that are being converted from inline to
extent mapped.

## References
- https://git.kernel.org/stable/c/131294c35ed6f777bd4e79d42af13b5c41bf2775
- https://git.kernel.org/stable/c/6f4200ec76a0d31200c308ec5a71c68df5417004
- https://git.kernel.org/stable/c/81b915181c630ee1cffa052e52874fe4e1ba91ac
- https://git.kernel.org/stable/c/9404839e0c9db5a517ea83c0ca3388b39d105fdf
- https://git.kernel.org/stable/c/c0c8edbc8abbe8f16d80a1d794d1ba2c12b6f193
- https://git.kernel.org/stable/c/d440d6427a5e3a877c1c259b8d2b216ddb65e185
- https://git.kernel.org/stable/c/f83391339d8493b9ff24167516aaa5a5e88d8f81
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50286.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50286
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
