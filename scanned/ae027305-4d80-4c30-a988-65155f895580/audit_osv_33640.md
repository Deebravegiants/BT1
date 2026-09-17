# [C] Apache NuttX RTOS: tools/bdf-converter.: tools/bdf-converter: Fix loop termination condition.

## Summary
Severity: Critical
Advisory: CVE-2025-47868
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/CVE-2025-47868
Type: osv

## Details
Out-of-bounds Write resulting in possible Heap-based Buffer Overflow vulnerability was discovered in tools/bdf-converter font conversion utility that is part of Apache NuttX RTOS repository. This standalone program is optional and neither part of NuttX RTOS nor Applications runtime, but active bdf-converter users may be affected when this tool is exposed to external provided user data data (i.e. publicly available automation).

This issue affects Apache NuttX: from 6.9 before 12.9.0.

Users are recommended to upgrade to version 12.9.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/06/14/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47868.json
- https://lists.apache.org/thread/p4o2lcqgspx3ws1n2p4wmoqbqow1w1pw
- https://nvd.nist.gov/vuln/detail/CVE-2025-47868
- https://github.com/apache/nuttx/pull/16000
