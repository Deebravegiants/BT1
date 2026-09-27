# [H] Apache Kylin Server-Side Request Forgery (SSRF) Vulnerability

## Summary
Severity: High
Advisory: GHSA-f6m8-qm7j-fh65
CVE: CVE-2025-61735
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-10-02
Source: https://github.com/advisories/GHSA-f6m8-qm7j-fh65
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin` — affected >=4.0.0 <5.0.3
- Maven: `org.apache.kylin:kylin-common-server` — affected >=4.0.0 <5.0.3
- Maven: `org.apache.kylin:kylin-common-service` — affected >=4.0.0 <5.0.3
- Maven: `org.apache.kylin:kylin-core-common` — affected >=4.0.0 <5.0.3
- Maven: `org.apache.kylin:kylin-core-metadata` — affected >=4.0.0 <5.0.3
- Maven: `org.apache.kylin:kylin-ops-server` — affected >=4.0.0 <5.0.3
- Maven: `org.apache.kylin:kylin-server` — affected >=4.0.0 <5.0.3

## Details
Server-Side Request Forgery (SSRF) vulnerability in Apache Kylin.

This issue affects Apache Kylin: from 4.0.0 through 5.0.2. You are fine as long as the Kylin's system and project admin access is well protected.

Users are recommended to upgrade to version 5.0.3, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61735
- https://github.com/apache/kylin/pull/2332
- https://github.com/apache/kylin/commit/22eb8fd5dfdeffa3fc57bae6d5c82a019eece662
- https://github.com/apache/kylin
- https://issues.apache.org/jira/browse/KYLIN-6082
- https://lists.apache.org/thread/yscobmx869zvprsykb94r24jtmb58ckh
- http://www.openwall.com/lists/oss-security/2025/09/30/9
