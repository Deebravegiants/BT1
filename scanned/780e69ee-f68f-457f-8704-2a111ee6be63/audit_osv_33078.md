# [H] hfs: fix slab-out-of-bounds in hfs_bnode_read()

## Summary
Severity: High
Advisory: CVE-2025-38715
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38715
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

hfs: fix slab-out-of-bounds in hfs_bnode_read()

This patch introduces is_bnode_offset_valid() method that checks
the requested offset value. Also, it introduces
check_and_correct_requested_length() method that checks and
correct the requested length (if it is necessary). These methods
are used in hfs_bnode_read(), hfs_bnode_write(), hfs_bnode_clear(),
hfs_bnode_copy(), and hfs_bnode_move() with the goal to prevent
the access out of allocated memory and triggering the crash.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/384a66b89f9540a9a8cb0f48807697dfabaece4c
- https://git.kernel.org/stable/c/67ecc81f6492275c9c54280532f558483c99c90e
- https://git.kernel.org/stable/c/a1a60e79502279f996e55052f50cc14919020475
- https://git.kernel.org/stable/c/a431930c9bac518bf99d6b1da526a7f37ddee8d8
- https://git.kernel.org/stable/c/e7d2dc2421e821e4045775e6dc226378328de6f6
- https://git.kernel.org/stable/c/eec522fd0d28106b14a59ab2d658605febe4a3bb
- https://git.kernel.org/stable/c/efc095b35b23297e419c2ab4fc1ed1a8f0781a29
- https://git.kernel.org/stable/c/fc7f732984ec91f30be3e574e0644066d07f2b78
- https://git.kernel.org/stable/c/fe2891a9c43ab87d1a210d61e6438ca6936e2f62
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38715.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38715
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
