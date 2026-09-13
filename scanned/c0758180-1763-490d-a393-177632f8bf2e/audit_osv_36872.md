# [M] Wazuh: Heap-based NULL WRITE Buffer Underflow in GetAlertData

## Summary
Severity: Medium
Advisory: CVE-2026-26204
Aliases: GHSA-j4c7-hwjw-8857
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-26204
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From version 1.0.0 to before version 4.14.4, a heap-based out-of-bounds WRITE occurs in GetAlertData, resulting in writing a NULL byte exactly 1 byte before the start of the buffer allocated by strdup. Due to unsigned integer underflow and pointer arithmetic wrapping, the write lands at offset -1 from the buffer, corrupting heap metadata. A malicious actor can potentially leverage this issue through a compromised agent to cause denial of service or heap corruption by injecting a specially crafted alert into the alerts log file monitored by wazuh-logcollector. This issue has been patched in version 4.14.4.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26204.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-j4c7-hwjw-8857
- https://nvd.nist.gov/vuln/detail/CVE-2026-26204
