# [H] Wildfly-elytron possibly vulnerable to timing attacks via use of unsafe comparator

## Summary
Severity: High
Advisory: GHSA-jmj6-p2j9-68cp
CVE: CVE-2022-3143
CWE: CWE-203, CWE-208
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-01-13
Source: https://github.com/advisories/GHSA-jmj6-p2j9-68cp
Type: github-advisory

## Affected
- Maven: `org.wildfly.security:wildfly-elytron` — affected >=0 <1.15.15.Final
- Maven: `org.wildfly.security:wildfly-elytron` — affected >=1.16.0.CR1 <1.20.3.Final

## Details
wildfly-elytron: possible timing attacks via use of unsafe comparator. A flaw was found in Wildfly-elytron. Wildfly-elytron uses `java.util.Arrays.equals` in several places, which is unsafe and vulnerable to timing attacks. To compare values securely, use `java.security.MessageDigest.isEqual` instead. This flaw allows an attacker to access secure information or impersonate an authed user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3143
- https://access.redhat.com/security/cve/CVE-2022-3143
- https://bugzilla.redhat.com/show_bug.cgi?id=2124682
- https://github.com/wildfly-security/wildfly-elytron
