# [M] Apache Livy: Restrict file access 

## Summary
Severity: Medium
Advisory: GHSA-hm8x-rpgg-7855
CVE: CVE-2025-60012
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-hm8x-rpgg-7855
Type: github-advisory

## Affected
- Maven: `org.apache.livy:livy-server` — affected >=0.7.0-incubating <0.9.0-incubating

## Details
Malicious configuration can lead to unauthorized file access in Apache Livy.

This issue affects Apache Livy 0.7.0 and 0.8.0 when connecting to Apache Spark 3.1 or later.

A request that includes a Spark configuration value supported from Apache Spark version 3.1 can lead to users gaining access to files they do not have permissions to.

For the vulnerability to be exploitable, the user needs to have access to Apache Livy's REST or JDBC interface and be able to send requests with arbitrary Spark configuration values.

Users are recommended to upgrade to version 0.9.0 or later, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60012
- https://github.com/apache/incubator-livy
- https://lists.apache.org/thread/gpc85fwrgrbglpk9gm8tmcjzqnctx64w
- http://www.openwall.com/lists/oss-security/2026/03/12/1
