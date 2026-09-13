# [H] nvme-pci: fix out-of-bounds access in nvme_setup_descriptor_pools

## Summary
Severity: High
Advisory: CVE-2026-74383
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74383
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-pci: fix out-of-bounds access in nvme_setup_descriptor_pools

nvme_setup_descriptor_pools() indexes dev->descriptor_pools[] using the
numa_node forwarded from hctx->numa_node by its single caller,
nvme_init_hctx_common().  On a non-NUMA kernel hctx->numa_node is
NUMA_NO_NODE (-1).  Because the parameter was declared 'unsigned', the
value becomes UINT_MAX and the index walks off the array (sized to
nr_node_ids), faulting during nvme_alloc_ns() and leaving the namespace
without a /dev node.

Reproduces on any NVMe controller probed by a CONFIG_NUMA=n kernel:

  BUG: unable to handle page fault for address: ffff889101603d38
  RIP: 0010:nvme_init_hctx_common+0x5a/0x190 [nvme]
  Call Trace:
   nvme_init_hctx+0x10/0x20 [nvme]
   nvme_alloc_ns+0x9e/0xa10 [nvme_core]
   nvme_scan_ns+0x301/0x3b0 [nvme_core]
   nvme_scan_ns_async+0x23/0x30 [nvme_core]

Switch the parameter to int and fall back to node 0 when it is
NUMA_NO_NODE; node 0 is always present.

## References
- https://git.kernel.org/stable/c/3e8aed5edaeeb237f97255d711aac6b5843fc059
- https://git.kernel.org/stable/c/a192b8cfa447e1b3701a13434a31c392b2e7ed29
- https://git.kernel.org/stable/c/fa9b6accd1ad7af6914b409c6b003c417724c299
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74383.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74383
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
