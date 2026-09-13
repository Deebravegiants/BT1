# [H] exfat: validate cluster allocation bits of the allocation bitmap

## Summary
Severity: High
Advisory: CVE-2025-40307
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40307
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

exfat: validate cluster allocation bits of the allocation bitmap

syzbot created an exfat image with cluster bits not set for the allocation
bitmap. exfat-fs reads and uses the allocation bitmap without checking
this. The problem is that if the start cluster of the allocation bitmap
is 6, cluster 6 can be allocated when creating a directory with mkdir.
exfat zeros out this cluster in exfat_mkdir, which can delete existing
entries. This can reallocate the allocated entries. In addition,
the allocation bitmap is also zeroed out, so cluster 6 can be reallocated.
This patch adds exfat_test_bitmap_range to validate that clusters used for
the allocation bitmap are correctly marked as in-use.

## References
- https://git.kernel.org/stable/c/13c1d24803d5b0446b3f6f0fdd67e07ac1fdc7bf
- https://git.kernel.org/stable/c/67ce8034dc0278ddd88cad93d4218a945180dddd
- https://git.kernel.org/stable/c/6bc58b4c53795ab5fe00648344aa7d9d61175f90
- https://git.kernel.org/stable/c/79c1587b6cda74deb0c86fc7ba194b92958c793c
- https://git.kernel.org/stable/c/87f827d53bd0688597bda63ae95908e2ad39bac0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40307.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40307
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
