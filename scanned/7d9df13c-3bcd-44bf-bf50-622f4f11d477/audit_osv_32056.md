# [H] wifi: ath11k: update channel list in reg notifier instead reg worker

## Summary
Severity: High
Advisory: CVE-2025-23133
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-23133
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.12.46, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: update channel list in reg notifier instead reg worker

Currently when ath11k gets a new channel list, it will be processed
according to the following steps:
1. update new channel list to cfg80211 and queue reg_work.
2. cfg80211 handles new channel list during reg_work.
3. update cfg80211's handled channel list to firmware by
ath11k_reg_update_chan_list().

But ath11k will immediately execute step 3 after reg_work is just
queued. Since step 2 is asynchronous, cfg80211 may not have completed
handling the new channel list, which may leading to an out-of-bounds
write error:
BUG: KASAN: slab-out-of-bounds in ath11k_reg_update_chan_list
Call Trace:
    ath11k_reg_update_chan_list+0xbfe/0xfe0 [ath11k]
    kfree+0x109/0x3a0
    ath11k_regd_update+0x1cf/0x350 [ath11k]
    ath11k_regd_update_work+0x14/0x20 [ath11k]
    process_one_work+0xe35/0x14c0

Should ensure step 2 is completely done before executing step 3. Thus
Wen raised patch[1]. When flag NL80211_REGDOM_SET_BY_DRIVER is set,
cfg80211 will notify ath11k after step 2 is done.

So enable the flag NL80211_REGDOM_SET_BY_DRIVER then cfg80211 will
notify ath11k after step 2 is done. At this time, there will be no
KASAN bug during the execution of the step 3.

[1] https://patchwork.kernel.org/project/linux-wireless/patch/20230201065313.27203-1-quic_wgong@quicinc.com/

Tested-on: WCN6855 hw2.0 PCI WLAN.HSP.1.1-03125-QCAHSPSWPL_V1_V2_SILICONZ_LITE-3

## References
- https://git.kernel.org/stable/c/26618c039b78a76c373d4e02c5fbd52e3a73aead
- https://git.kernel.org/stable/c/933ab187e679e6fbdeea1835ae39efcc59c022d2
- https://git.kernel.org/stable/c/f952fb83c9c6f908d27500764c4aee1df04b9d3f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23133.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
