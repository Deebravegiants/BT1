# [M] wifi: iwlwifi: mvm: don't try to talk to a dead firmware

## Summary
Severity: Medium
Advisory: CVE-2025-21930
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21930
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: don't try to talk to a dead firmware

This fixes:

 bad state = 0
 WARNING: CPU: 10 PID: 702 at drivers/net/wireless/inel/iwlwifi/iwl-trans.c:178 iwl_trans_send_cmd+0xba/0xe0 [iwlwifi]
 Call Trace:
  <TASK>
  ? __warn+0xca/0x1c0
  ? iwl_trans_send_cmd+0xba/0xe0 [iwlwifi 64fa9ad799a0e0d2ba53d4af93a53ad9a531f8d4]
  iwl_fw_dbg_clear_monitor_buf+0xd7/0x110 [iwlwifi 64fa9ad799a0e0d2ba53d4af93a53ad9a531f8d4]
  _iwl_dbgfs_fw_dbg_clear_write+0xe2/0x120 [iwlmvm 0e8adb18cea92d2c341766bcc10b18699290068a]

Ask whether the firmware is alive before sending a command.

## References
- https://git.kernel.org/stable/c/437e93ecd40754f9e938d524daf52a10c589e2d4
- https://git.kernel.org/stable/c/d73d2c6e3313f0ba60711ab4f4b9044eddca9ca5
- https://git.kernel.org/stable/c/e7c31a3f4f27d61b9ccd894a7bf4690f137da0ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21930.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21930
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
