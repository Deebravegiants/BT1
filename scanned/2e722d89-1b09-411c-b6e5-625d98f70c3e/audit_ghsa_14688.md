# [H] Apache Hive: Deserialization of untrusted data when fetching partitions from the Metastore

## Summary
Severity: High
Advisory: GHSA-6hqr-c69m-r76q
CVE: CVE-2022-41137
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2024-12-05
Source: https://github.com/advisories/GHSA-6hqr-c69m-r76q
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive-exec` — affected >=4.0.0-alpha-1 <4.0.0-alpha-2

## Details
Apache Hive Metastore (HMS) uses SerializationUtilities#deserializeObjectWithTypeInformation method when filtering and fetching partitions that is unsafe and can lead to Remote Code Execution (RCE) since it allows the deserialization of arbitrary data.

In real deployments, the vulnerability can be exploited only by authenticated users/clients that were able to successfully establish a connection to the Metastore. From an API perspective any code that calls the unsafe method may be vulnerable unless it performs additional prerechecks on the input arguments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41137
- https://github.com/apache/hive/commit/60027bb9c91a93affcfebd9068f064bc1f2a74c9
- https://github.com/apache/hive
- https://issues.apache.org/jira/browse/HIVE-26539
- https://lists.apache.org/thread/jwtr3d9yovf2wo0qlxvkhoxnwxxyzgts
- http://www.openwall.com/lists/oss-security/2024/12/04/2
