# [H] The Undertow module of WildFly allows source code disclosure

## Summary
Severity: High
Advisory: GHSA-4vwv-x3gp-2j4g
CVE: CVE-2015-3198
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4vwv-x3gp-2j4g
Type: github-advisory

## Affected
- Maven: `org.wildfly:wildfly-parent` — affected >=8.1.0.Final <9.0.0.CR2

## Details
The Undertow module of WildFly versions  8.1.0.Final, 8.2.0.Final, 9.0.0.CR1  allows remote attackers to obtain the source code of a JSP page via a "/" at the end of a URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3198
- https://bugzilla.redhat.com/show_bug.cgi?id=1224787
- https://developer.jboss.org/message/927301#927301
- https://issues.jboss.org/browse/WFLY-4595
- https://stackoverflow.com/questions/30028346/with-trailing-slash-in-url-jsp-show-source-code
