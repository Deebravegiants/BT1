# [M] Apache Jackrabbit: Core and JCR Commons are vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Medium
Advisory: GHSA-cxvc-g8f2-4gmm
CVE: CVE-2025-58782
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-cxvc-g8f2-4gmm
Type: github-advisory

## Affected
- Maven: `org.apache.jackrabbit:jackrabbit-core` — affected >=1.0.0 <2.22.2
- Maven: `org.apache.jackrabbit:jackrabbit-jcr-commons` — affected >=1.0.0 <2.22.2

## Details
There is a serialization of Untrusted Data vulnerability in Apache Jackrabbit Core and Apache Jackrabbit JCR Commons.

This issue affects Apache Jackrabbit Core: from 1.0.0 through 2.22.1; Apache Jackrabbit JCR Commons: from 1.0.0 through 2.22.1.

Deployments that accept JNDI URIs for JCR lookup from untrusted users allows them to inject malicious JNDI references, potentially leading to arbitrary code execution through deserialization of untrusted data. Users are recommended to upgrade to version 2.22.2. JCR lookup through JNDI has been disabled by default in 2.22.2. Users of this feature need to enable it explicitly and are adviced to review their use of JNDI URI for JCR lookup.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-58782
- https://github.com/apache/jackrabbit/pull/229
- https://github.com/apache/jackrabbit
- https://issues.apache.org/jira/browse/JCR-5135
- https://lists.apache.org/thread/t4wdrost6dh17dh406g792j9wq6xmy6v
- http://www.openwall.com/lists/oss-security/2025/09/06/3
