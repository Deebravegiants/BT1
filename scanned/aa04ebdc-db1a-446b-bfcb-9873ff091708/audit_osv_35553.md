# [H] Out-of-bounds write in Bluetooth HFP Hands-Free CIND indicator parsing (cind_handle_values)

## Summary
Severity: High
Advisory: CVE-2026-10641
Aliases: GHSA-wx5j-q6f2-59p3
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-10641
Type: osv

## Details
Zephyr's Bluetooth Classic Hands-Free Profile (HFP) Hands-Free role parser (subsys/bluetooth/host/classic/hfp_hf.c) contains an out-of-bounds write. During Service Level Connection setup the HF sends AT+CIND=? and parses the AG's +CIND: response in cind_handle(), which assigns a per-entry counter index and calls cind_handle_values() for each list element. cind_handle_values() then wrote hf->ind_table[index] = i without verifying that index is within the 20-element int8_t ind_table[] array of struct bt_hfp_hf. Because the parser places no cap on the number of +CIND: list entries, a remote Attendant Gateway (a malicious, compromised, or spoofed peer the device connects to over Bluetooth) can send a response with more than 20 recognized indicator entries and drive index arbitrarily large, writing a small attacker-positioned value past the array into adjacent struct fields (feature masks, SDP/version state, the calls[] array, work/atomic bookkeeping) and potentially beyond the static connection pool slot. This yields memory corruption and at least denial of service of the Bluetooth host, triggered by a single malformed AT response with no user interaction. The sibling consumer ag_indicator_handle_values() already performed the equivalent bounds check; this commit adds the same index >= ARRAY_SIZE(hf->ind_table) guard to close the gap. Affects builds with CONFIG_BT_HFP_HF enabled; introduced with the original HFP HF CIND parser (~v1.7) and present through v4.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10641.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-wx5j-q6f2-59p3
- https://nvd.nist.gov/vuln/detail/CVE-2026-10641
- https://github.com/zephyrproject-rtos/zephyr/commit/cf7693a8261ae363c9cf46cfd51005486637173e
- https://github.com/zephyrproject-rtos/zephyr
