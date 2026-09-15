# [C] Apache Avro Java SDK: Arbitrary Code Execution when reading Avro Data (Java SDK)

## Summary
Severity: Critical
Advisory: GHSA-r7pg-v2c8-mfg3
CVE: CVE-2024-47561
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-r7pg-v2c8-mfg3
Type: github-advisory

## Affected
- Maven: `org.apache.avro:avro` — affected >=0 <1.11.4

## Details
Schema parsing in the Java SDK of Apache Avro 1.11.3 and previous versions allows bad actors to execute arbitrary code.
Users are recommended to upgrade to version 1.11.4 or 1.12.0, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47561
- https://github.com/apache/avro/pull/2934
- https://github.com/apache/avro/pull/2980
- https://github.com/apache/avro/commit/8f89868d29272e3afea2ff8de8c85cb81a57d900
- https://github.com/apache/avro/commit/f6b3bd7e50e6e09fedddb98c61558c022ba31285
- https://github.com/apache/avro
- https://issues.apache.org/jira/browse/AVRO-3985
- https://lists.apache.org/thread/c2v7mhqnmq0jmbwxqq3r5jbj1xg43h5x
- https://security.netapp.com/advisory/ntap-20241011-0003
- https://thehackernews.com/2024/10/critical-apache-avro-sdk-flaw-allows.html
- https://www.openwall.com/lists/oss-security/2024/10/03/1
- http://www.openwall.com/lists/oss-security/2024/10/03/1
