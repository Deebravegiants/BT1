# [H] ipc: fix to protect IPCS lookups using RCU

## Summary
Severity: High
Advisory: CVE-2025-38212
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38212
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipc: fix to protect IPCS lookups using RCU

syzbot reported that it discovered a use-after-free vulnerability, [0]

[0]: https://lore.kernel.org/all/67af13f8.050a0220.21dd3.0038.GAE@google.com/

idr_for_each() is protected by rwsem, but this is not enough.  If it is
not protected by RCU read-critical region, when idr_for_each() calls
radix_tree_node_free() through call_rcu() to free the radix_tree_node
structure, the node will be freed immediately, and when reading the next
node in radix_tree_for_each_slot(), the already freed memory may be read.

Therefore, we need to add code to make sure that idr_for_each() is
protected within the RCU read-critical region when we call it in
shm_destroy_orphaned().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/5180561afff8e0f029073c8c8117c95c6512d1f9
- https://git.kernel.org/stable/c/5f1e1573bf103303944fd7225559de5d8297539c
- https://git.kernel.org/stable/c/68c173ea138b66d7dd1fd980c9bc578a18e11884
- https://git.kernel.org/stable/c/74bc813d11c30e28fc5261dc877cca662ccfac68
- https://git.kernel.org/stable/c/78297d53d3878d43c1d627d20cd09f611fa4b91d
- https://git.kernel.org/stable/c/b0b6bf90ce2699a574b3683e22c44d0dcdd7a057
- https://git.kernel.org/stable/c/b968ba8bfd9f90914957bbbd815413bf6a98eca7
- https://git.kernel.org/stable/c/d66adabe91803ef34a8b90613c81267b5ded1472
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38212.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38212
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
