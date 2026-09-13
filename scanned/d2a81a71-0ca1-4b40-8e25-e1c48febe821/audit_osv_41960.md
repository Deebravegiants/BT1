# [H] wifi: iwlwifi: mvm: fix driver-set TX rates on old devices

## Summary
Severity: High
Advisory: CVE-2026-64176
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64176
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: fix driver-set TX rates on old devices

On old devices such as 7265D, rates are still encoded in version 1
format, which doesn't use the CCK/OFDM rate index (0-3/0-7) but
rather their PLCP value (e.g. 10 for 1 Mbps CCK rate.)

While introducing v3 rates, I changed the driver from internally
handling v1 rates and converting to v2, to internally handling v3
and converting to v1 or v2 according to the firmware. I accordingly
changed the code in iwl_mvm_mac80211_idx_to_hwrate() to no longer
have different values for different APIs. This was correct.

However, I later reverted this part of the change, because it was
reported that I had broken beacon rates, causing a FW assert/crash.
This caused TX_CMD rates to be set incorrectly, potentially causing
a warning when reported back from the device as having been used.

Fix this (hopefully correctly now) by handling beacon rates in the
TX_CMD that's embedded in the beacon template command separately.
Restore iwl_mvm_mac80211_idx_to_hwrate() to return only the rate
index, not PLCP value, fixing the real TX_CMD.

## References
- https://git.kernel.org/stable/c/6b58a79f2cd98156856eb49e8b55db5facdd7e6d
- https://git.kernel.org/stable/c/6fe92651b44fd3cfc8dcfdaad0e82885c384dada
- https://git.kernel.org/stable/c/fb84b5cbcaab3ca0f4e961d92a40ed7f3aac483b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64176.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64176
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
