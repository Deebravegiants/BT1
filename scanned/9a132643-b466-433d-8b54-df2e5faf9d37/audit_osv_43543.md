# [H] ocfs2: reject FITRIM ranges shorter than a cluster

## Summary
Severity: High
Advisory: CVE-2026-74349
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74349
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: reject FITRIM ranges shorter than a cluster

ocfs2_trim_mainbm() trims the global bitmap in cluster units, but its
too-short range validation only checks sb->s_blocksize.

On filesystems with a cluster size larger than the block size, a FITRIM
range that is at least one block but shorter than one cluster is accepted
and shifted down to len == 0.  The later start + len - 1 and len -= ... 
arithmetic then underflows and can drive trimming past the requested
range.

Reject ranges shorter than s_clustersize instead.  That preserves the
existing -EINVAL behavior for requests that cannot discard even one
allocation unit and keeps zero-cluster trims out of the group walk.

## References
- https://git.kernel.org/stable/c/06c0a0431b9856506fcd9b2c1b0c6136567d756d
- https://git.kernel.org/stable/c/2c13e02592b918be7725ab5965e01ef4e46c4b57
- https://git.kernel.org/stable/c/346314bb0cc2fc52b50b73d6ecc62e0217455c2e
- https://git.kernel.org/stable/c/3fa7139b5f42731a61f78c42433adae13f9adc21
- https://git.kernel.org/stable/c/441abb77222f155e8d931dbabb465466db01cfd7
- https://git.kernel.org/stable/c/ca1afd88f5eaaff9168e1466e5401385edf59543
- https://git.kernel.org/stable/c/d903d59c0315f59bdf0214b4f13d71c9feb2c45c
- https://git.kernel.org/stable/c/e652d0f5108e447b22da4249bcd23dd1b63c73dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74349.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74349
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
