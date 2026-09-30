# [H] wifi: ath11k: Ignore frags from uninitialized peer in dp.

## Summary
Severity: High
Advisory: CVE-2023-53822
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53822
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: Ignore frags from uninitialized peer in dp.

When max virtual ap interfaces are configured in all the bands with
ACS and hostapd restart is done every 60s, a crash is observed at
random times.
In this certain scenario, a fragmented packet is received for
self peer, for which rx_tid and rx_frags are not initialized in
datapath. While handling this fragment, crash is observed as the
rx_frag list is uninitialised and when we walk in
ath11k_dp_rx_h_sort_frags, skb null leads to exception.

To address this, before processing received fragments we check
dp_setup_done flag is set to ensure that peer has completed its
dp peer setup for fragment queue, else ignore processing the
fragments.

Call trace:
  ath11k_dp_process_rx_err+0x550/0x1084 [ath11k]
  ath11k_dp_service_srng+0x70/0x370 [ath11k]
  0xffffffc009693a04
  __napi_poll+0x30/0xa4
  net_rx_action+0x118/0x270
  __do_softirq+0x10c/0x244
  irq_exit+0x64/0xb4
  __handle_domain_irq+0x88/0xac
  gic_handle_irq+0x74/0xbc
  el1_irq+0xf0/0x1c0
  arch_cpu_idle+0x10/0x18
  do_idle+0x104/0x248
  cpu_startup_entry+0x20/0x64
  rest_init+0xd0/0xdc
  arch_call_rest_init+0xc/0x14
  start_kernel+0x480/0x4b8
  Code: f9400281 f94066a2 91405021 b94a0023 (f9406401)

Tested-on: IPQ8074 hw2.0 AHB WLAN.HK.2.7.0.1-01744-QCAHKSWPL_SILICONZ-1

## References
- https://git.kernel.org/stable/c/41efc47f5bc53e63461579e206adc17c4452ab6e
- https://git.kernel.org/stable/c/a06bfb3c9f69f303692cdae87bc0899d2ae8b2a6
- https://git.kernel.org/stable/c/e78526a06b53718bfc1dfff37864c7760e41f8ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53822.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53822
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
