# [H] fs/ntfs3: Fix oob in ntfs_listxattr

## Summary
Severity: High
Advisory: CVE-2023-52640
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2023-52640
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Fix oob in ntfs_listxattr

The length of name cannot exceed the space occupied by ea.

## References
- https://git.kernel.org/stable/c/0830c5cf19bdec50d0ede4755ddc463663deb21c
- https://git.kernel.org/stable/c/52fff5799e3d1b5803ecd2f5f19c13c65f4f7b23
- https://git.kernel.org/stable/c/6ed6cdbe88334ca3430c5aee7754dc4597498dfb
- https://git.kernel.org/stable/c/731ab1f9828800df871c5a7ab9ffe965317d3f15
- https://git.kernel.org/stable/c/a585faf0591548fe0920641950ebfa8a6eefe1cd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52640.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52640
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
