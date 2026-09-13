# [H] lib/generic-radix-tree.c: Fix rare race in __genradix_ptr_alloc()

## Summary
Severity: High
Advisory: CVE-2024-47668
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-47668
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

lib/generic-radix-tree.c: Fix rare race in __genradix_ptr_alloc()

If we need to increase the tree depth, allocate a new node, and then
race with another thread that increased the tree depth before us, we'll
still have a preallocated node that might be used later.

If we then use that node for a new non-root node, it'll still have a
pointer to the old root instead of being zeroed - fix this by zeroing it
in the cmpxchg failure path.

## References
- https://git.kernel.org/stable/c/0f078f8ca93b28a34e20bd050f12cd4efeee7c0f
- https://git.kernel.org/stable/c/0f27f4f445390cb7f73d4209cb2bf32834dc53da
- https://git.kernel.org/stable/c/99418ec776a39609f50934720419e0b464ca2283
- https://git.kernel.org/stable/c/ad5ee9feebc2eb8cfc76ed74a2d6e55343b0e169
- https://git.kernel.org/stable/c/b2f11c6f3e1fc60742673b8675c95b78447f3dae
- https://git.kernel.org/stable/c/d942e855324a60107025c116245095632476613e
- https://git.kernel.org/stable/c/ebeff038744c498a036e7a92eb8e433ae0a386d7
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47668.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47668
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
