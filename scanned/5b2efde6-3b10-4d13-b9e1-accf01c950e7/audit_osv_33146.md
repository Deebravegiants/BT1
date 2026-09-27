# [H] btrfs: abort transaction on unexpected eb generation at btrfs_copy_root()

## Summary
Severity: High
Advisory: CVE-2025-39800
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-39800
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: abort transaction on unexpected eb generation at btrfs_copy_root()

If we find an unexpected generation for the extent buffer we are cloning
at btrfs_copy_root(), we just WARN_ON() and don't error out and abort the
transaction, meaning we allow to persist metadata with an unexpected
generation. Instead of warning only, abort the transaction and return
-EUCLEAN.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/33e8f24b52d2796b8cfb28c19a1a7dd6476323a8
- https://git.kernel.org/stable/c/4290e34fb87ae556b12c216efd0ae91583446b7a
- https://git.kernel.org/stable/c/4734255ef39b416864139dcda96a387fe5f33a6a
- https://git.kernel.org/stable/c/da2124719f386b6e5d4d4b1a2e67c440e4d5892f
- https://git.kernel.org/stable/c/f4f5bd9251a4cbe55aaa05725c6c3c32ad1f74b3
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39800.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39800
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
