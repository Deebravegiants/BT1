# [H] wifi: ath11k: use work queue to process beacon tx event

## Summary
Severity: High
Advisory: CVE-2024-47724
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47724
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: use work queue to process beacon tx event

Commit 3a415daa3e8b ("wifi: ath11k: add P2P IE in beacon template")
from Feb 28, 2024 (linux-next), leads to the following Smatch static
checker warning:

drivers/net/wireless/ath/ath11k/wmi.c:1742 ath11k_wmi_p2p_go_bcn_ie()
warn: sleeping in atomic context

The reason is that ath11k_bcn_tx_status_event() will directly call might
sleep function ath11k_wmi_cmd_send() during RCU read-side critical
sections. The call trace is like:

ath11k_bcn_tx_status_event()
-> rcu_read_lock()
-> ath11k_mac_bcn_tx_event()
	-> ath11k_mac_setup_bcn_tmpl()
	……
		-> ath11k_wmi_bcn_tmpl()
			-> ath11k_wmi_cmd_send()
-> rcu_read_unlock()

Commit 886433a98425 ("ath11k: add support for BSS color change") added the
ath11k_mac_bcn_tx_event(), commit 01e782c89108 ("ath11k: fix warning
of RCU usage for ath11k_mac_get_arvif_by_vdev_id()") added the RCU lock
to avoid warning but also introduced this BUG.

Use work queue to avoid directly calling ath11k_mac_bcn_tx_event()
during RCU critical sections. No need to worry about the deletion of vif
because cancel_work_sync() will drop the work if it doesn't start or
block vif deletion until the running work is done.

Tested-on: WCN6855 hw2.0 PCI WLAN.HSP.1.1-03125-QCAHSPSWPL_V1_V2_SILICONZ_LITE-3.6510.30

## References
- https://git.kernel.org/stable/c/177b49dbf9c1d8f9f25a22ffafa416fc2c8aa6a3
- https://git.kernel.org/stable/c/6db232905e094e64abff1f18249905d068285e09
- https://git.kernel.org/stable/c/dbd51da69dda1137723b8f66460bf99a9dac8dd2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47724.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47724
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
