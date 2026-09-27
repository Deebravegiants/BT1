# [C] net: ethernet: mtk_eth_soc: pass eth to mtk_handle_irq_rx in poll_controller

## Summary
Severity: Critical
Advisory: CVE-2026-80694
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80694
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: mtk_eth_soc: pass eth to mtk_handle_irq_rx in poll_controller

mtk_handle_irq_rx expects a struct mtk_eth * (matching the request_irq
cookie), but mtk_poll_controller incorrectly passed the net_device *.
Calling ndo_poll_controller with CONFIG_NET_POLL_CONTROLLER enabled
would then crash.

## References
- https://git.kernel.org/stable/c/276f1f180f55d56cf5992a581e20ed2b3dfa6ced
- https://git.kernel.org/stable/c/3bd58ac9ca0c552651f533c1bd280dd19ae7d4e8
- https://git.kernel.org/stable/c/7eb46318d53940dab63dea7130e720b67a656104
- https://git.kernel.org/stable/c/e095f249e2209674f6366f6db0383a2b96e19239
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80694.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80694
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
