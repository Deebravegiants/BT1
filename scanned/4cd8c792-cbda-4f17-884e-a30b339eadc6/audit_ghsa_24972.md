# [M] OpenID4Java does not verify that Attribute Exchange (AX) information is signed

## Summary
Severity: Medium
Advisory: GHSA-j473-c3rr-rx9p
CVE: CVE-2011-4314
CWE: CWE-20, CWE-345
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j473-c3rr-rx9p
Type: github-advisory

## Affected
- Maven: `org.openid4java:openid4java` — affected >=0 <0.9.6

## Details
message/ax/AxMessage.java in OpenID4Java before 0.9.6 final, as used in JBoss Enterprise Application Platform 5.1 before 5.1.2, Step2, Kay Framework before 1.0.2, and possibly other products does not verify that Attribute Exchange (AX) information is signed, which allows remote attackers to modify potentially sensitive AX information without detection via a man-in-the-middle (MITM) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4314
- https://github.com/jbufu/openid4java
- https://issues.jboss.org/browse/JBEPP-1368
- https://issues.jboss.org/browse/SOA-3597
- https://web.archive.org/web/20201207151157/http://securitytracker.com/id?1026400
- http://openid.net/2011/05/05/attribute-exchange-security-alert
- http://rhn.redhat.com/errata/RHSA-2012-0441.html
- http://rhn.redhat.com/errata/RHSA-2012-0519.html
- http://www.openwall.com/lists/oss-security/2011/11/16/1
- http://www.openwall.com/lists/oss-security/2011/11/17/1
- http://www.redhat.com/support/errata/RHSA-2011-1804.html
