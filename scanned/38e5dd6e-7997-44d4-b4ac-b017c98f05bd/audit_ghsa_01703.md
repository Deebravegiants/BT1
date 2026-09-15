# [H] Potential remote code execution in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-344f-f5vg-2jfj
CVE: CVE-2020-9484
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-21
Source: https://github.com/advisories/GHSA-344f-f5vg-2jfj
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=10.0.0-M1 <10.0.0-M5
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=9.0.0 <9.0.35
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=8.0.0 <8.5.55
- Maven: `org.apache.tomcat:tomcat-catalina` — affected >=7.0.0 <7.0.104
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.0.0-M1 <10.0.0-M5
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0 <9.0.35
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.0.0 <8.5.55
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=7.0.0 <7.0.104

## Details
When using Apache Tomcat versions 10.0.0-M1 to 10.0.0-M4, 9.0.0.M1 to 9.0.34, 8.5.0 to 8.5.54 and 7.0.0 to 7.0.103 if a) an attacker is able to control the contents and name of a file on the server; and b) the server is configured to use the PersistenceManager with a FileStore; and c) the PersistenceManager is configured with sessionAttributeValueClassNameFilter="null" (the default unless a SecurityManager is used) or a sufficiently lax filter to allow the attacker provided object to be deserialized; and d) the attacker knows the relative file path from the storage location used by FileStore to the file the attacker has control over; then, using a specifically crafted request, the attacker will be able to trigger remote code execution via deserialization of the file under their control. Note that all of conditions a) to d) must be true for the attack to succeed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9484
- https://github.com/apache/tomcat/commit/3aa8f28db7efb311cdd1b6fe15a9cd3b167a2222.patch
- https://github.com/apache/tomcat/commit/4785433a226a20df6acbea49296e1ce7e23de453
- https://github.com/apache/tomcat/commit/6d66e99ef85da93e4d2c2a536ca51aa3418bfaf4
- https://github.com/apache/tomcat/commit/74b105657ffbd1d1de80455f03446c3bbf30d1f5
- https://github.com/apache/tomcat/commit/93f0cc403a9210d469afc2bd9cf03ab3251c6f35
- https://github.com/apache/tomcat/commit/bb33048e3f9b4f2b70e4da2e6c4e34ca89023b1b
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WJ7XHKWJWDNWXUJH6UB7CLIW4TWOZ26N
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GIQHXENTLYUNOES4LXVNJ2NCUQQRF5VJ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJ7XHKWJWDNWXUJH6UB7CLIW4TWOZ26N
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GIQHXENTLYUNOES4LXVNJ2NCUQQRF5VJ
- https://lists.debian.org/debian-lts-announce/2020/07/msg00010.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00026.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00020.html
- https://lists.apache.org/thread.html/rfe62fbf9d4c314f166fe8c668e50e5d9dd882a99447f26f0367474bf@%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rfe62fbf9d4c314f166fe8c668e50e5d9dd882a99447f26f0367474bf@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rfe62fbf9d4c314f166fe8c668e50e5d9dd882a99447f26f0367474bf@%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rfe62fbf9d4c314f166fe8c668e50e5d9dd882a99447f26f0367474bf@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rfe62fbf9d4c314f166fe8c668e50e5d9dd882a99447f26f0367474bf%40%3Cusers.tomcat.apache.org%3E
