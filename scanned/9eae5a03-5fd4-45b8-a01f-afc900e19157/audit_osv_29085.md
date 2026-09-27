# [H] bcache: fix variable length array abuse in btree_iter

## Summary
Severity: High
Advisory: CVE-2024-39482
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39482
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.94, >=6.2.0 <6.6.34, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bcache: fix variable length array abuse in btree_iter

btree_iter is used in two ways: either allocated on the stack with a
fixed size MAX_BSETS, or from a mempool with a dynamic size based on the
specific cache set. Previously, the struct had a fixed-length array of
size MAX_BSETS which was indexed out-of-bounds for the dynamically-sized
iterators, which causes UBSAN to complain.

This patch uses the same approach as in bcachefs's sort_iter and splits
the iterator into a btree_iter with a flexible array member and a
btree_iter_stack which embeds a btree_iter as well as a fixed-length
data array.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/0c31344e22dd8d6b1394c6e4c41d639015bdc671
- https://git.kernel.org/stable/c/2c3d7b03b658dc8bfa6112b194b67b92a87e081b
- https://git.kernel.org/stable/c/3a861560ccb35f2a4f0a4b8207fa7c2a35fc7f31
- https://git.kernel.org/stable/c/5a1922adc5798b7ec894cd3f197afb6f9591b023
- https://git.kernel.org/stable/c/6479b9f41583b013041943c4602e1ad61cec8148
- https://git.kernel.org/stable/c/934e1e4331859183a861f396d7dfaf33cb5afb02
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39482.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39482
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
