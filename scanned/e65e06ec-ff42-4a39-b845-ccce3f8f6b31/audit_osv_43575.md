# [H] wifi: ath11k: cancel SSR work items during PCI shutdown

## Summary
Severity: High
Advisory: CVE-2026-74407
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74407
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: cancel SSR work items during PCI shutdown

A reboot can crash the kernel if it overlaps with WLAN firmware crash
recovery (SSR). The crash is a NULL pointer dereference in the MHI teardown
path while freeing DMA-backed MHI contexts.

Simplified trace:
  dma_free_attrs
  mhi_deinit_dev_ctxt [mhi]
  ath11k_pci_power_down [ath11k_pci]
  ath11k_pci_shutdown [ath11k_pci]
  device_shutdown
  kernel_restart

On the host side, SSR is driven by the MHI RDDM callback, which queues
reset_work to perform device recovery. reset_work power-cycles the device
by calling ath11k_hif_power_down() followed by ath11k_hif_power_up(). The
power-down phase deinitializes MHI and frees DMA resources.

Shutdown/reboot runs fully asynchronously with this RDDM-driven SSR
recovery flow. As a result, the shutdown path
(ath11k_pci_shutdown() -> ath11k_pci_power_down()) can race with the SSR
recovery sequence.

Fix this by canceling SSR-related work items during PCI shutdown, marking
the device as unregistering, and serializing the RDDM callback path that
checks and queues reset_work. This ensures that no new SSR recovery work
can be queued once teardown has started, and that any in-flight recovery
work is fully synchronized before device power-down, preventing MHI
teardown and DMA resource freeing from running more than once.

Note: This issue only affects PCI/MHI-based devices. AHB-based ath11k
devices do not queue reset_work in normal SSR flows.

Tested-on: WCN6855 hw2.1 PCI WLAN.HSP.1.1-04866.5-QCAHSPSWPL_V1_V2_SILICONZ_IOE-1

## References
- https://git.kernel.org/stable/c/53dd29e8aeb2a1b5f079178551836b85fc6b53df
- https://git.kernel.org/stable/c/8c79aac429b583301f387374ff37c59be671df87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74407.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74407
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
