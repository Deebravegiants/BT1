# [M] CVE-2026-48684

## Summary
Severity: Medium
Advisory: CVE-2026-48684
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48684
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 contains an out-of-bounds read in the NetFlow v9 options template parser. In process_netflow_v9_options_template() (src/netflow_plugin/netflow_v9_collector.cpp), the scope parsing loop (lines 224-229) iterates until scopes_offset reaches the attacker-controlled option_scope_length value, reading netflow9_template_flowset_record_t structures at each step. No bounds check validates that (zone_address + scopes_offset + sizeof(record)) stays within the flowset. The same issue affects the options field loop (lines 241-257) with option_length. Furthermore, option_scope_length is not validated to be a multiple of sizeof(netflow9_template_flowset_record_t), potentially causing misaligned reads. An attacker can trigger reads past the end of the UDP packet buffer.

## References
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/netflow_plugin/netflow_v9_collector.cpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48684.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48684
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48684-netflow-v9-options-oob
