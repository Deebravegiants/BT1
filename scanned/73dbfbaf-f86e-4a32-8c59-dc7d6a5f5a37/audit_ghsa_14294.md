# [H] Apache James server's JMX management service vulnerable to privilege escalation by local user

## Summary
Severity: High
Advisory: GHSA-w7r6-v4j7-h94w
CVE: CVE-2023-26269
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-03
Source: https://github.com/advisories/GHSA-w7r6-v4j7-h94w
Type: github-advisory

## Affected
- Maven: `org.apache.james:javax-mail-extension` — affected >=0 <3.7.4

## Details
Apache James server version 3.7.3 and earlier provides a JMX management service without authentication by default. This allows privilege escalation by a malicious local user. Administrators are advised to disable JMX, or set up a JMX password. Note that version 3.7.4 onward will set up a JMX password automatically for Guice users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26269
- https://github.com/apache/james-project
- https://lists.apache.org/thread/2z44rg93pflbjhvbwy3xtz505bx41cbs
- http://www.openwall.com/lists/oss-security/2023/04/18/3
