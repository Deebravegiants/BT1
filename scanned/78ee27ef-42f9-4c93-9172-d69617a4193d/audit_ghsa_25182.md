# [M] Jenkins Groovy Postbuild Plugin vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-38ch-x695-m794
CVE: CVE-2018-1000202
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-38ch-x695-m794
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:groovy-postbuild` — affected >=0 <2.4

## Details
A persisted cross-site scripting vulnerability exists in Jenkins Groovy Postbuild Plugin 2.3.1 and older in various Jelly files that allows attackers able to control build badge content to define JavaScript that would be executed in another user's browser when that other user performs some UI actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000202
- https://jenkins.io/security/advisory/2018-05-09/#SECURITY-821
