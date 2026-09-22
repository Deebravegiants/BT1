# [C] net: stmmac: fix the crash issue for zero copy XDP_TX action

## Summary
Severity: Critical
Advisory: CVE-2025-71095
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71095
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: stmmac: fix the crash issue for zero copy XDP_TX action

There is a crash issue when running zero copy XDP_TX action, the crash
log is shown below.

[  216.122464] Unable to handle kernel paging request at virtual address fffeffff80000000
[  216.187524] Internal error: Oops: 0000000096000144 [#1]  SMP
[  216.301694] Call trace:
[  216.304130]  dcache_clean_poc+0x20/0x38 (P)
[  216.308308]  __dma_sync_single_for_device+0x1bc/0x1e0
[  216.313351]  stmmac_xdp_xmit_xdpf+0x354/0x400
[  216.317701]  __stmmac_xdp_run_prog+0x164/0x368
[  216.322139]  stmmac_napi_poll_rxtx+0xba8/0xf00
[  216.326576]  __napi_poll+0x40/0x218
[  216.408054] Kernel panic - not syncing: Oops: Fatal exception in interrupt

For XDP_TX action, the xdp_buff is converted to xdp_frame by
xdp_convert_buff_to_frame(). The memory type of the resulting xdp_frame
depends on the memory type of the xdp_buff. For page pool based xdp_buff
it produces xdp_frame with memory type MEM_TYPE_PAGE_POOL. For zero copy
XSK pool based xdp_buff it produces xdp_frame with memory type
MEM_TYPE_PAGE_ORDER0. However, stmmac_xdp_xmit_back() does not check the
memory type and always uses the page pool type, this leads to invalid
mappings and causes the crash. Therefore, check the xdp_buff memory type
in stmmac_xdp_xmit_back() to fix this issue.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/3f7823219407f2f18044c2b72366a48810c5c821
- https://git.kernel.org/stable/c/45ee0462b88396a0bd1df1991f801c89994ea72b
- https://git.kernel.org/stable/c/4d0ceb7677e1c4616afb96abb4518f70b65abb0d
- https://git.kernel.org/stable/c/5e5988736a95b1de7f91b10ac2575454b70e4897
- https://git.kernel.org/stable/c/a48e232210009be50591fdea8ba7c07b0f566a13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71095.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71095
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
