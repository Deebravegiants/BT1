# [M] Apache Avro Java SDK is Vulnerable to Code Injection

## Summary
Severity: Medium
Advisory: GHSA-rp46-r563-jrc7
CVE: CVE-2025-33042
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-rp46-r563-jrc7
Type: github-advisory

## Affected
- Maven: `org.apache.avro:avro-compiler` — affected >=1.12.0 <1.12.1
- Maven: `org.apache.avro:avro-compiler` — affected >=0 <1.11.5

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability in Apache Avro Java SDK when generating specific records from untrusted Avro schemas.

This issue affects Apache Avro Java SDK: all versions through 1.11.4 and version 1.12.0.

Users are recommended to upgrade to version 1.12.1 or 1.11.5, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-33042
- https://github.com/apache/avro/pull/3150
- https://github.com/apache/avro/commit/84bc7322ca1c04ab4a8e4e708acf1e271541aac4
- https://github.com/apache/avro
- https://github.com/pypa/advisory-database/tree/main/vulns/avro/PYSEC-2026-26.yaml
- https://issues.apache.org/jira/browse/AVRO-4053
- https://lists.apache.org/thread/fy88wmgf1lj9479vrpt12cv8x73lroj1
- https://security.snyk.io/vuln/SNYK-JAVA-ORGAPACHEAVRO-15282783
- http://www.openwall.com/lists/oss-security/2026/02/12/2
