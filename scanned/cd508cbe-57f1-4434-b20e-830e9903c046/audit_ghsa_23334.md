# [M] Jenkins SSH Build Agents Plugin did not verify host keys

## Summary
Severity: Medium
Advisory: GHSA-x654-4wjh-74q6
CVE: CVE-2017-2648
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x654-4wjh-74q6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ssh-slaves` — affected >=0 <1.15

## Details
It was found that jenkins-ssh-slaves-plugin before version 1.15 did not perform host key verification, thereby enabling Man-in-the-Middle attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2648
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2648
- https://jenkins.io/security/advisory/2017-03-20
- http://www.securityfocus.com/bid/96985
