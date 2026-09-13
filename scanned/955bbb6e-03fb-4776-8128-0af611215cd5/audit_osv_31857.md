# [H] idpf: fix checksums set in idpf_rx_rsc()

## Summary
Severity: High
Advisory: CVE-2025-21890
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-21890
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.18, >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

idpf: fix checksums set in idpf_rx_rsc()

idpf_rx_rsc() uses skb_transport_offset(skb) while the transport header
is not set yet.

This triggers the following warning for CONFIG_DEBUG_NET=y builds.

DEBUG_NET_WARN_ON_ONCE(!skb_transport_header_was_set(skb))

[   69.261620] WARNING: CPU: 7 PID: 0 at ./include/linux/skbuff.h:3020 idpf_vport_splitq_napi_poll (include/linux/skbuff.h:3020) idpf
[   69.261629] Modules linked in: vfat fat dummy bridge intel_uncore_frequency_tpmi intel_uncore_frequency_common intel_vsec_tpmi idpf intel_vsec cdc_ncm cdc_eem cdc_ether usbnet mii xhci_pci xhci_hcd ehci_pci ehci_hcd libeth
[   69.261644] CPU: 7 UID: 0 PID: 0 Comm: swapper/7 Tainted: G S      W          6.14.0-smp-DEV #1697
[   69.261648] Tainted: [S]=CPU_OUT_OF_SPEC, [W]=WARN
[   69.261650] RIP: 0010:idpf_vport_splitq_napi_poll (include/linux/skbuff.h:3020) idpf
[   69.261677] ? __warn (kernel/panic.c:242 kernel/panic.c:748)
[   69.261682] ? idpf_vport_splitq_napi_poll (include/linux/skbuff.h:3020) idpf
[   69.261687] ? report_bug (lib/bug.c:?)
[   69.261690] ? handle_bug (arch/x86/kernel/traps.c:285)
[   69.261694] ? exc_invalid_op (arch/x86/kernel/traps.c:309)
[   69.261697] ? asm_exc_invalid_op (arch/x86/include/asm/idtentry.h:621)
[   69.261700] ? __pfx_idpf_vport_splitq_napi_poll (drivers/net/ethernet/intel/idpf/idpf_txrx.c:4011) idpf
[   69.261704] ? idpf_vport_splitq_napi_poll (include/linux/skbuff.h:3020) idpf
[   69.261708] ? idpf_vport_splitq_napi_poll (drivers/net/ethernet/intel/idpf/idpf_txrx.c:3072) idpf
[   69.261712] __napi_poll (net/core/dev.c:7194)
[   69.261716] net_rx_action (net/core/dev.c:7265)
[   69.261718] ? __qdisc_run (net/sched/sch_generic.c:293)
[   69.261721] ? sched_clock (arch/x86/include/asm/preempt.h:84 arch/x86/kernel/tsc.c:288)
[   69.261726] handle_softirqs (kernel/softirq.c:561)

## References
- https://git.kernel.org/stable/c/4279bbebe00ffdbfd1a77567961886e35465cbdc
- https://git.kernel.org/stable/c/57e68f256911f3ab4b997141975561646ccbbb8c
- https://git.kernel.org/stable/c/674fcb4f4a7e3e277417a01788cc6daae47c3804
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21890.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21890
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
