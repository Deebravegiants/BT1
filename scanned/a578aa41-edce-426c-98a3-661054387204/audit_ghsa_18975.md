# [C] Apache Causeway vulnerable to deserialization in Java

## Summary
Severity: Critical
Advisory: GHSA-wq4c-57mh-5f7g
CVE: CVE-2025-64408
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-wq4c-57mh-5f7g
Type: github-advisory

## Affected
- Maven: `org.apache.causeway.commons:causeway-commons` — affected >=0 <3.5.0
- Maven: `org.apache.causeway.core:causeway-applib` — affected >=0 <3.5.0
- Maven: `org.apache.causeway.core:causeway-core` — affected >=0 <3.5.0
- Maven: `org.apache.causeway.viewer:causeway-viewer-wicket` — affected >=0 <3.5.0

## Details
Apache Causeway faces Java deserialization vulnerabilities that allow remote code execution (RCE) through user-controllable URL parameters. These vulnerabilities affect all applications using Causeway's ViewModel functionality and can be exploited by authenticated attackers to execute arbitrary code with application privileges. 

This issue affects all current versions.

Users are recommended to upgrade to version 3.5.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64408
- https://github.com/apache/causeway/commit/bef00f58d2a2cba9a45230c9d117a0327e4c7038
- https://github.com/apache/causeway/commit/e66290fe9be87aa0e4c5dc55bce1993a54330624
- https://github.com/apache/causeway/commit/e6bf00c63c33cfa894a19d6122526a1aec227d14
- https://github.com/apache/causeway
- https://issues.apache.org/jira/browse/CAUSEWAY-3939
- https://lists.apache.org/thread/rjlg4spqhmgy1xgq9wq5h2tfnq4pm70b
- http://www.openwall.com/lists/oss-security/2025/11/19/1
