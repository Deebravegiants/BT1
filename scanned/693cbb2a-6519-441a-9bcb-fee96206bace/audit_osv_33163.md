# [H] net: rose: include node references in rose_neigh refcount

## Summary
Severity: High
Advisory: CVE-2025-39827
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39827
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.1.150, >=6.2.0 <6.6.104, >=6.7.0 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: rose: include node references in rose_neigh refcount

Current implementation maintains two separate reference counting
mechanisms: the 'count' field in struct rose_neigh tracks references from
rose_node structures, while the 'use' field (now refcount_t) tracks
references from rose_sock.

This patch merges these two reference counting systems using 'use' field
for proper reference management. Specifically, this patch adds incrementing
and decrementing of rose_neigh->use when rose_neigh->count is incremented
or decremented.

This patch also modifies rose_rt_free(), rose_rt_device_down() and
rose_clear_route() to properly release references to rose_neigh objects
before freeing a rose_node through rose_remove_node().

These changes ensure rose_neigh structures are properly freed only when
all references, including those from rose_node structures, are released.
As a result, this resolves a slab-use-after-free issue reported by Syzbot.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/384210cceb1873a4c8218b27ba0745444436b728
- https://git.kernel.org/stable/c/4cce478c3e82a5fc788d72adb2f4c4e983997639
- https://git.kernel.org/stable/c/9c547c8eee9d1cf6e744611d688b9f725cf9a115
- https://git.kernel.org/stable/c/d7563b456ed44151e1a82091d96f60166daea89b
- https://git.kernel.org/stable/c/da9c9c877597170b929a6121a68dcd3dd9a80f45
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39827.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39827
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
