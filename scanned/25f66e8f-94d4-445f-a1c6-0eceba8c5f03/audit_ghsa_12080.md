# [C] Apache Ranger has a Code Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-c87w-642h-m97h
CVE: CVE-2025-59059
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-c87w-642h-m97h
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger-plugins-common` — affected >=0 <2.8.0

## Details
Remote Code Execution Vulnerability in NashornScriptEngineCreator is reported in Apache Ranger versions <= 2.7.0.

Users are recommended to upgrade to version 2.8.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59059
- https://github.com/apache/ranger
- https://lists.apache.org/thread/z47q86rho80390lf2qcmoc2josvs0gtv
- http://www.openwall.com/lists/oss-security/2026/03/02/5
