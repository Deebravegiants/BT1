# [H] Incorrect Authorization in WildFly Elytron

## Summary
Severity: High
Advisory: GHSA-qgrq-cx4c-2rmm
CVE: CVE-2020-1748
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-qgrq-cx4c-2rmm
Type: github-advisory

## Affected
- Maven: `org.wildfly.security:wildfly-elytron` — affected >=0 <1.6.8

## Details
A flaw was found in all supported versions before wildfly-elytron-1.6.8.Final-redhat-00001, where the WildFlySecurityManager checks were bypassed when using custom security managers, resulting in an improper authorization. This flaw leads to information exposure by unauthenticated access to secure resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1748
- https://bugzilla.redhat.com/show_bug.cgi?id=1807707
- https://security.netapp.com/advisory/ntap-20201001-0005
