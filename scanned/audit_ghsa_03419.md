# [M] Missing Authentication for Critical Function in Apache Calcite

## Summary
Severity: Medium
Advisory: GHSA-hxp5-8pgq-mgv9
CVE: CVE-2020-13955
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-hxp5-8pgq-mgv9
Type: github-advisory

## Affected
- Maven: `org.apache.calcite:calcite-core` — affected >=0 <1.26.0
- Maven: `org.apache.calcite:calcite-druid` — affected >=0 <1.26.0
- Maven: `org.apache.calcite:calcite-splunk` — affected >=0 <1.26.0

## Details
"HttpUtils#getURLConnection method disables explicitly hostname verification for HTTPS connections making clients vulnerable to man-in-the-middle attacks. Calcite uses this method internally to connect with Druid and Splunk so information leakage may happen when using the respective Calcite adapters. The method itself is in a utility class so people may use it to create vulnerable HTTPS connections for other applications. From Apache Calcite 1.26 onwards, the hostname verification will be performed using the default JVM truststore."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13955
- https://github.com/apache/calcite/commit/43eeafcbac29d02c72bd520c003cdfc571de2d15
- https://issues.apache.org/jira/browse/CALCITE-4298
- https://lists.apache.org/thread.html/r0b0fbe2038388175951ce1028182d980f9e9a7328be13d52dab70bb3%40%3Cdev.calcite.apache.org%3E
