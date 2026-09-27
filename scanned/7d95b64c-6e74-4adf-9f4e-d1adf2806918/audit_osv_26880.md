# [H] wifi: iwlwifi: dvm: Fix memcpy: detected field-spanning write backtrace

## Summary
Severity: High
Advisory: CVE-2023-54286
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54286
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: dvm: Fix memcpy: detected field-spanning write backtrace

A received TKIP key may be up to 32 bytes because it may contain
MIC rx/tx keys too. These are not used by iwl and copying these
over overflows the iwl_keyinfo.key field.

Add a check to not copy more data to iwl_keyinfo.key then will fit.

This fixes backtraces like this one:

 memcpy: detected field-spanning write (size 32) of single field "sta_cmd.key.key" at drivers/net/wireless/intel/iwlwifi/dvm/sta.c:1103 (size 16)
 WARNING: CPU: 1 PID: 946 at drivers/net/wireless/intel/iwlwifi/dvm/sta.c:1103 iwlagn_send_sta_key+0x375/0x390 [iwldvm]
 <snip>
 Hardware name: Dell Inc. Latitude E6430/0H3MT5, BIOS A21 05/08/2017
 RIP: 0010:iwlagn_send_sta_key+0x375/0x390 [iwldvm]
 <snip>
 Call Trace:
  <TASK>
  iwl_set_dynamic_key+0x1f0/0x220 [iwldvm]
  iwlagn_mac_set_key+0x1e4/0x280 [iwldvm]
  drv_set_key+0xa4/0x1b0 [mac80211]
  ieee80211_key_enable_hw_accel+0xa8/0x2d0 [mac80211]
  ieee80211_key_replace+0x22d/0x8e0 [mac80211]
 <snip>

## References
- https://git.kernel.org/stable/c/3ed3c1c2fc3482b72e755820261779cd2e2c5a3e
- https://git.kernel.org/stable/c/57189c885149825be8eb8c3524b5af017fdeb941
- https://git.kernel.org/stable/c/6cd644f66b43709816561d63e0173cb0c7aab159
- https://git.kernel.org/stable/c/76b5ea43ad2fb4f726ddfaff839430a706e7d7c2
- https://git.kernel.org/stable/c/87940e4030e4705e1f3fd2bbb1854eae8308314b
- https://git.kernel.org/stable/c/91ad1ab3cc7e981cb6d6ee100686baed64e1277e
- https://git.kernel.org/stable/c/ef16799640865f937719f0771c93be5dca18adc6
- https://git.kernel.org/stable/c/fa57021262e998e2229d6383b1081638df2fe238
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54286.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54286
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
