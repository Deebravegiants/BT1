# [H] hv_netvsc: use kmap_local_page in netvsc_copy_to_send_buf

## Summary
Severity: High
Advisory: CVE-2026-53199
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53199
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

hv_netvsc: use kmap_local_page in netvsc_copy_to_send_buf

netvsc_copy_to_send_buf() copies page buffer entries into the VMBus
send buffer using phys_to_virt() on the entry PFN. Entries for the
RNDIS header and the skb linear data come from kmalloc'd memory and
are always in the kernel direct map, but entries for skb fragments
reference page cache or user pages, which on 32-bit x86 with
CONFIG_HIGHMEM=y can live above the LOWMEM boundary. For such a page
phys_to_virt() returns an address outside the direct map and the
subsequent memcpy() faults on the transmit softirq path, which is
fatal.

Map the pages with kmap_local_page() instead, handling two properties
of the page buffer entries:

 - pb[i].pfn is a Hyper-V PFN at HV_HYP_PAGE_SIZE (4K) granularity,
   not a native PFN. Reconstruct the physical address first and derive
   the native page from it, so the mapping stays correct where
   PAGE_SIZE > HV_HYP_PAGE_SIZE (e.g. arm64 with 64K pages).

 - Since commit 41a6328b2c55 ("hv_netvsc: Preserve contiguous PFN
   grouping in the page buffer array"), an entry describes a full
   physically contiguous fragment and pb[i].len can exceed PAGE_SIZE,
   while kmap_local_page() maps a single page. Copy page by page,
   splitting at native page boundaries.

The copy path only handles packets smaller than the send section size
(6144 bytes by default); larger packets take the cp_partial path where
only the RNDIS header is copied. So entries here are bounded by the
section size and a copy is split at most once on 4K-page systems. On
!CONFIG_HIGHMEM configs kmap_local_page() folds to page_address() and
no mapping work is added.

## References
- https://git.kernel.org/stable/c/004e9ecfe6c5384f9e0b2f6f6389d42ec22789af
- https://git.kernel.org/stable/c/09b8a7aa5a341bb345dc492aac139525efa13515
- https://git.kernel.org/stable/c/0b38870d81ab3a04c1ab0598d9d3285f5d9d0584
- https://git.kernel.org/stable/c/16514afeb7d3d121072ba9a0b640d6c1c5507db0
- https://git.kernel.org/stable/c/695c59cf7bf707e6ff8cea01916ee50e86616933
- https://git.kernel.org/stable/c/918c0c988239aa5ab96b254e504d191af6191061
- https://git.kernel.org/stable/c/a82d4251918f37d9c5aab7b365157669fb885ec3
- https://git.kernel.org/stable/c/fe7221b4346418d27ec2daccfc09df6692b76f0b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53199.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53199
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
