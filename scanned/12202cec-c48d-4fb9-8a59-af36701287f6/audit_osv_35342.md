# [H] wifi: rtlwifi: 8192cu: fix tid out of range in rtl92cu_tx_fill_desc()

## Summary
Severity: High
Advisory: CVE-2025-71100
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71100
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtlwifi: 8192cu: fix tid out of range in rtl92cu_tx_fill_desc()

TID getting from ieee80211_get_tid() might be out of range of array size
of sta_entry->tids[], so check TID is less than MAX_TID_COUNT. Othwerwise,
UBSAN warn:

 UBSAN: array-index-out-of-bounds in drivers/net/wireless/realtek/rtlwifi/rtl8192cu/trx.c:514:30
 index 10 is out of range for type 'rtl_tid_data [9]'

## References
- https://git.kernel.org/stable/c/90a15ff324645aa806d81fa349497cd964861b66
- https://git.kernel.org/stable/c/9765d6eb8298b07d499cdf9ef7c237d3540102d6
- https://git.kernel.org/stable/c/dd39edb445f07400e748da967a07d5dca5c5f96e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71100.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71100
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
