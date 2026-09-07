# [H] Jenkins Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-5j46-5hwq-gwh7
CVE: CVE-2023-43495
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-5j46-5hwq-gwh7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.50 <2.414.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.415 <2.424

## Details
`ExpandableDetailsNote` allows annotating build log content with additional information that can be revealed when interacted with.

Jenkins 2.423 and earlier, LTS 2.414.1 and earlier does not escape the value of the `caption` constructor parameter of `ExpandableDetailsNote`.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to provide `caption` parameter values.

As of publication, the related API is not used within Jenkins (core), and the Jenkins security team is not aware of any affected plugins.
Jenkins 2.424, LTS 2.414.2 escapes `caption` constructor parameter values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43495
- https://www.jenkins.io/security/advisory/2023-09-20/#SECURITY-3245
- http://www.openwall.com/lists/oss-security/2023/09/20/5
