# [C] camel-ldap component allows LDAP Injection when using the filter option

## Summary
Severity: Critical
Advisory: GHSA-w66j-xc7r-m2jv
CVE: CVE-2022-45046
CWE: CWE-90
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-w66j-xc7r-m2jv
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-ldap` — affected >=0 <3.14.6
- Maven: `org.apache.camel:camel-ldap` — affected >=3.15.0 <3.18.4

## Details
The camel-ldap component allows LDAP Injection when using the filter option. Users are recommended to either move to the Camel-Spring-Ldap component (which is not affected) or upgrade to 3.14.6 or 3.18.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45046
- https://camel.apache.org/security/CVE-2022-45046.html
- https://github.com/apache/camel
- http://www.openwall.com/lists/oss-security/2022/12/05/2
