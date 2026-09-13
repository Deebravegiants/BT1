# [M] CVE-2026-48683

## Summary
Severity: Medium
Advisory: CVE-2026-48683
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48683
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 contains an out-of-bounds read vulnerability in the NetFlow v9 data flowset processor. In src/netflow_plugin/netflow_v9_collector.cpp, the Data template branch (lines 1695-1702) iterates over flow records without performing a per-iteration bounds check against the packet end pointer. In contrast, the Options template branch (lines 1709-1719) correctly checks 'if (pkt + offset + field_template->total_length > packet_end)' before each iteration. The Data branch omits this check entirely. Since template definitions are sent by the network peer (and are unauthenticated UDP), an attacker can craft templates that cause the parser to read arbitrary memory past the packet buffer. This can leak sensitive memory contents or cause a crash.

## References
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/netflow_plugin/netflow_v9_collector.cpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48683.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48683
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48683-netflow-v9-data-oob
