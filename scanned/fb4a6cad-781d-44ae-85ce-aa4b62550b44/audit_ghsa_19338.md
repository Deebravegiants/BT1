# [H] Apache InLong: JDBC Vulnerability during verification processing

## Summary
Severity: High
Advisory: GHSA-r324-vgr5-73c9
CVE: CVE-2025-27522
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-r324-vgr5-73c9
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.13.0 <2.2.0

## Details
Deserialization of Untrusted Data vulnerability in Apache InLong.

This issue affects Apache InLong: from 1.13.0 through 2.1.0. This vulnerability is a secondary mining bypass for CVE-2024-26579. Users are advised to upgrade to Apache InLong's 2.2.0 or cherry-pick [1] to solve it.

[1] 

 https://github.com/apache/inlong/pull/11732

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27522
- https://github.com/apache/inlong/pull/11732
- https://github.com/apache/inlong/commit/86c893cfd8f7ba9ffce5d20abef6cd360f502fdf
- https://github.com/apache/inlong
- https://lists.apache.org/thread/s4dnmq3gwcjocxf85qk190knlzd26jby
