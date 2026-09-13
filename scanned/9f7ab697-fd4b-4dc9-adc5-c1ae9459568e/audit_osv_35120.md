# [H] fs/ntfs3: Initialize allocated memory before use

## Summary
Severity: High
Advisory: CVE-2025-68365
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68365
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.68, >=6.13.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Initialize allocated memory before use

KMSAN reports: Multiple uninitialized values detected:

- KMSAN: uninit-value in ntfs_read_hdr (3)
- KMSAN: uninit-value in bcmp (3)

Memory is allocated by __getname(), which is a wrapper for
kmem_cache_alloc(). This memory is used before being properly
cleared. Change kmem_cache_alloc() to kmem_cache_zalloc() to
properly allocate and clear memory before use.

## References
- https://git.kernel.org/stable/c/192e8ce302f14ac66259231dd10cede19858d742
- https://git.kernel.org/stable/c/7d52c592cf53f5bb7163967edc01d2d7d80de44a
- https://git.kernel.org/stable/c/a58e29849aef8d26554a982989a2190b49aaf8ed
- https://git.kernel.org/stable/c/a8a3ca23bbd9d849308a7921a049330dc6c91398
- https://git.kernel.org/stable/c/bdf38063fd15f2fc7361dc0b5d3c259741eab835
- https://git.kernel.org/stable/c/f7728057220cabd720e27e46097edad48e5bd728
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68365.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68365
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
