# [M] wifi: ath11k: fix RCU stall while reaping monitor destination ring

## Summary
Severity: Medium
Advisory: CVE-2024-58097
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2024-58097
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.6.122, >=6.7.0 <6.12.68, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: fix RCU stall while reaping monitor destination ring

While processing the monitor destination ring, MSDUs are reaped from the
link descriptor based on the corresponding buf_id.

However, sometimes the driver cannot obtain a valid buffer corresponding
to the buf_id received from the hardware. This causes an infinite loop
in the destination processing, resulting in a kernel crash.

kernel log:
ath11k_pci 0000:58:00.0: data msdu_pop: invalid buf_id 309
ath11k_pci 0000:58:00.0: data dp_rx_monitor_link_desc_return failed
ath11k_pci 0000:58:00.0: data msdu_pop: invalid buf_id 309
ath11k_pci 0000:58:00.0: data dp_rx_monitor_link_desc_return failed

Fix this by skipping the problematic buf_id and reaping the next entry,
replacing the break with the next MSDU processing.

Tested-on: WCN6855 hw2.0 PCI WLAN.HSP.1.1-03125-QCAHSPSWPL_V1_V2_SILICONZ_LITE-3.6510.30
Tested-on: QCN9074 hw1.0 PCI WLAN.HK.2.7.0.1-01744-QCAHKSWPL_SILICONZ-1

## References
- https://git.kernel.org/stable/c/16c6c35c03ea73054a1f6d3302a4ce4a331b427d
- https://git.kernel.org/stable/c/8db5de0cf02fccf4c759aa58edbe65659daf607c
- https://git.kernel.org/stable/c/9f1a002f0171d27f3554e529f3c70df438f05dfe
- https://git.kernel.org/stable/c/b4991fc41745645f8050506f5a8578bd11e6b378
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58097.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58097
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
