# [H] wifi: iwlwifi: mld: validate sta_mask before ffs() in BA session handlers

## Summary
Severity: High
Advisory: CVE-2026-64255
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64255
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mld: validate sta_mask before ffs() in BA session handlers

Three BA session handlers use ffs(ba_data->sta_mask) - 1 to derive a
station ID without checking that sta_mask is non-zero. When sta_mask is
zero, ffs() returns 0 and the subtraction wraps to 0xFFFFFFFF, causing
an out-of-bounds access on fw_id_to_link_sta[].

Add WARN_ON_ONCE(!ba_data->sta_mask) guards before each ffs() call,
consistent with the existing check in iwl_mld_ampdu_rx_start().

## References
- https://git.kernel.org/stable/c/1de92789ce31e46fa7e7d8e89c90b19cdb1c103b
- https://git.kernel.org/stable/c/f056fc2b927448d37eca6b6cacc3d1b0f67b20d2
- https://git.kernel.org/stable/c/fe7f339f63c9dc4ca546ed7ac38ba4bb3a99dcfc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64255.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64255
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
