# [M] Wazuh: Cluster Protocol Memory Exhaustion (DoS) via unbounded receive_str allocation and div_msg_box accumulation

## Summary
Severity: Medium
Advisory: CVE-2026-44253
Aliases: GHSA-h5r8-gvhv-cmp2
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-44253
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 3.9.0 until 4.14.5 and 5.0.0-beta2, the Wazuh cluster protocol in framework/wazuh/core/cluster/common.py allows an authenticated cluster node to exhaust memory on the master. The receive_str() method accepts an attacker-controlled total for InBuffer without a maximum, so a new_str command can request a multi-gigabyte bytearray and repeated requests accumulate in in_str. The divided-message path also retains flag_divided fragments under unique counters in div_msg_box without a count, aggregate-size, or expiration limit. Exploitation can disrupt agent connectivity and alert processing across the monitored environment. This issue is fixed in versions 4.14.5 and 5.0.0-beta2.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44253.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-h5r8-gvhv-cmp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44253
- https://github.com/wazuh/wazuh/commit/d29c5c89a0e16477545ca27f4e06229021e3183c
- https://github.com/wazuh/wazuh/pull/35173
