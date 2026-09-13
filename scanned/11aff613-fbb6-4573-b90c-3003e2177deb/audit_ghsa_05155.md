# [H] Apache Shiro: LDAP DN Injection in DefaultLdapRealm

## Summary
Severity: High
Advisory: GHSA-x96m-rh44-vgv8
CVE: CVE-2026-49268
CWE: CWE-90
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/S:P/AU:Y/R:A/RE:L/U:Red (CVSS_V4)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-x96m-rh44-vgv8
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-core` — affected >=0 <2.2.1
- Maven: `org.apache.shiro:shiro-core` — affected >=3.0.0-alpha-0 <3.0.0-alpha-2

## Details
A remote attacker can inject LDAP special characters into the Distinguished Name (DN) construction in DefaultLdapRealm class. User-supplied username input is directly concatenated into the LDAP DN template without any escaping of RFC 2253 special characters. This allows an attacker to manipulate the DN structure used for LDAP bind authentication, potentially bypassing authentication or impersonating other users.

This issue affects all Apache Shiro versions through 2.2.0, and 3.0.0-alpha-1 when using DefaultLdapRealm
Upgrade to Apache Shiro 2.2.1 or 3.0.0-alpha-2 or later, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49268
- https://github.com/apache/shiro
- https://lists.apache.org/thread/svszql3od8td7hn6conyj2oq70v53b5s
- http://www.openwall.com/lists/oss-security/2026/06/17/8
