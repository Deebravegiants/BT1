# [C] net: ti: icssg-prueth: fix missing data copy and wrong recycle in ZC RX dispatch

## Summary
Severity: Critical
Advisory: CVE-2026-43039
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43039
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ti: icssg-prueth: fix missing data copy and wrong recycle in ZC RX dispatch

emac_dispatch_skb_zc() allocates a new skb via napi_alloc_skb() but
never copies the packet data from the XDP buffer into it. The skb is
passed up the stack containing uninitialized heap memory instead of
the actual received packet, leaking kernel heap contents to userspace.

Copy the received packet data from the XDP buffer into the skb using
skb_copy_to_linear_data().

Additionally, remove the skb_mark_for_recycle() call since the skb is
backed by the NAPI page frag allocator, not page_pool. Marking a
non-page_pool skb for recycle causes the free path to return pages to
a page_pool that does not own them, corrupting page_pool state.

The non-ZC path (emac_rx_packet) does not have these issues because it
uses napi_build_skb() to wrap the existing page_pool page directly,
requiring no copy, and correctly marks for recycle since the page comes
from page_pool_dev_alloc_pages().

## References
- https://git.kernel.org/stable/c/5597dd284ff8c556c0b00f6a34473677426e3f81
- https://git.kernel.org/stable/c/a968438d4fc17ee1dcdc3cfa490dcb5e7709cf76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43039.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43039
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
