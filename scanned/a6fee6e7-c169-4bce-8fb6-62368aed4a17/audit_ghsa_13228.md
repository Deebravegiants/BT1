# [H] Apache Avro Java SDK vulnerable to Improper Input Validation

## Summary
Severity: High
Advisory: GHSA-rhrv-645h-fjfh
CVE: CVE-2023-39410
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-29
Source: https://github.com/advisories/GHSA-rhrv-645h-fjfh
Type: github-advisory

## Affected
- Maven: `org.apache.avro:avro` — affected >=0 <1.11.3

## Details
When deserializing untrusted or corrupted data, it is possible for a reader to consume memory beyond the allowed constraints and thus lead to out of memory on the system.

This issue affects Java applications using Apache Avro Java SDK up to and including 1.11.2.  Users should update to apache-avro version 1.11.3 which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39410
- https://github.com/apache/avro/commit/a12a7e44ddbe060c3dc731863cad5c15f9267828
- https://github.com/apache/avro
- https://github.com/pypa/advisory-database/tree/main/vulns/avro/PYSEC-2023-188.yaml
- https://issues.apache.org/jira/browse/AVRO-3819
- https://lists.apache.org/thread/q142wj99cwdd0jo5lvdoxzoymlqyjdds
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://www.openwall.com/lists/oss-security/2023/09/29/6
- http://www.openwall.com/lists/oss-security/2023/09/29/6
