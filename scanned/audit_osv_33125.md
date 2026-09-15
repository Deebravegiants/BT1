# [H] wifi: ath11k: fix sleeping-in-atomic in ath11k_mac_op_set_bitrate_mask()

## Summary
Severity: High
Advisory: CVE-2025-39732
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-07
Source: https://osv.dev/vulnerability/CVE-2025-39732
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: fix sleeping-in-atomic in ath11k_mac_op_set_bitrate_mask()

ath11k_mac_disable_peer_fixed_rate() is passed as the iterator to
ieee80211_iterate_stations_atomic(). Note in this case the iterator is
required to be atomic, however ath11k_mac_disable_peer_fixed_rate() does
not follow it as it might sleep. Consequently below warning is seen:

BUG: sleeping function called from invalid context at wmi.c:304
Call Trace:
 <TASK>
 dump_stack_lvl
 __might_resched.cold
 ath11k_wmi_cmd_send
 ath11k_wmi_set_peer_param
 ath11k_mac_disable_peer_fixed_rate
 ieee80211_iterate_stations_atomic
 ath11k_mac_op_set_bitrate_mask.cold

Change to ieee80211_iterate_stations_mtx() to fix this issue.

Tested-on: WCN6855 hw2.0 PCI WLAN.HSP.1.1-03125-QCAHSPSWPL_V1_V2_SILICONZ_LITE-3.6510.30

## References
- https://git.kernel.org/stable/c/65c12b104cb942d588a1a093acc4537fb3d3b129
- https://git.kernel.org/stable/c/6bdef22d540258ca06f079f7b6ae100669a19b47
- https://git.kernel.org/stable/c/7d4d0db0dc9424de2bdc0b45e919e4892603356f
- https://git.kernel.org/stable/c/9c0e3144924c7db701575a73af341d33184afeaf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39732.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39732
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
