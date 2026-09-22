# [M] Apache NiFi: Potential Insertion of Sensitive Parameter Values in Debug Log

## Summary
Severity: Medium
Advisory: GHSA-v3vc-6qcv-4vrx
CVE: CVE-2024-52067
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N/AU:Y/R:U/V:D/RE:L/U:Green (CVSS_V4)
Published: 2025-02-11
Source: https://github.com/advisories/GHSA-v3vc-6qcv-4vrx
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-framework-core` — affected >=1.16.0 <1.28.1
- Maven: `org.apache.nifi:nifi-framework-core` — affected >=2.0.0-M1 <2.0.0

## Details
Apache NiFi 1.16.0 through 1.28.0 and 2.0.0-M1 through 2.0.0-M4 include optional debug logging of Parameter Context values during the flow synchronization process. An authorized administrator with access to change logging levels could enable debug logging for framework flow synchronization, causing the application to write Parameter names and values to the application log. Parameter Context values may contain sensitive information depending on application flow configuration. Deployments of Apache NiFi with the default Logback configuration do not log Parameter Context values. Upgrading to Apache NiFi 2.0.0 or 1.28.1 is the recommendation mitigation, eliminating Parameter value logging from the flow synchronization process regardless of the Logback configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52067
- https://github.com/apache/nifi/commit/5aed878c5d2a193cd2039c2e997bc3025046bc41
- https://github.com/apache/nifi/commit/c1108365949268631526d5016b1a163a82f8e9df
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-13971
- https://lists.apache.org/thread/9rz5rwn2zc7pfjq7ppqldqlc067tlcwd
- http://www.openwall.com/lists/oss-security/2024/11/20/2
