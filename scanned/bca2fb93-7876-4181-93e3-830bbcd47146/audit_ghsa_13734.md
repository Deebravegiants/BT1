# [C] Apache Derby: LDAP injection vulnerability in authenticator

## Summary
Severity: Critical
Advisory: GHSA-rcjc-c4pj-xxrp
CVE: CVE-2022-46337
CWE: CWE-74, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-20
Source: https://github.com/advisories/GHSA-rcjc-c4pj-xxrp
Type: github-advisory

## Affected
- Maven: `org.apache.derby:derby` — affected >=10.1.1.0
- Maven: `org.apache.derby:derby` — affected >=10.2.1.6
- Maven: `org.apache.derby:derby` — affected >=10.3.1.4
- Maven: `org.apache.derby:derby` — affected >=10.4.1.3
- Maven: `org.apache.derby:derby` — affected >=10.5.1.1
- Maven: `org.apache.derby:derby` — affected >=10.6.1.0
- Maven: `org.apache.derby:derby` — affected 10.7.1.1
- Maven: `org.apache.derby:derby` — affected >=10.8.1.2
- Maven: `org.apache.derby:derby` — affected 10.9.1.0
- Maven: `org.apache.derby:derby` — affected >=10.10.1.1
- Maven: `org.apache.derby:derby` — affected 10.11.1.1
- Maven: `org.apache.derby:derby` — affected 10.12.1.1
- Maven: `org.apache.derby:derby` — affected 10.13.1.1
- Maven: `org.apache.derby:derby` — affected >=10.14.2.0 <10.14.2.1
- Maven: `org.apache.derby:derby` — affected >=10.16.1.1 <10.16.1.2
- Maven: `org.apache.derby:derby` — affected >=10.15.1.3 <10.15.2.1

## Details
A cleverly devised username might bypass LDAP authentication checks. In LDAP-authenticated Derby installations, this could let an attacker fill up the disk by creating junk Derby databases. In LDAP-authenticated Derby installations, this could also allow the attacker to execute malware which was visible to and executable by the account which booted the Derby server. In LDAP-protected databases which weren't also protected by SQL GRANT/REVOKE authorization, this vulnerability could also let an attacker view and corrupt sensitive data and run sensitive database functions and procedures.

Mitigation:

Users should upgrade to Java 21 and Derby 10.17.1.0.

Alternatively, users who wish to remain on older Java versions should build their own Derby distribution from one of the release families to which the fix was backported: 10.16, 10.15, and 10.14. Those are the releases which correspond, respectively, with Java LTS versions 17, 11, and 8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46337
- https://github.com/apache/derby
- https://issues.apache.org/jira/browse/DERBY-7147
- https://lists.apache.org/thread/q23kvvtoohgzwybxpwozmvvk17rp0td3
