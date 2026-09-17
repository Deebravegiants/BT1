# [M] Password stored in a recoverable format by Jenkins OpenId Connect Authentication Plugin 

## Summary
Severity: Medium
Advisory: GHSA-6r5w-jjr5-qvgr
CVE: CVE-2023-50770
CWE: CWE-312, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-6r5w-jjr5-qvgr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:oic-auth` — affected >=0 <4.229.vf736b

## Details
Jenkins OpenId Connect Authentication Plugin stores a password of a local user account used as an anti-lockout feature in a recoverable format, allowing attackers with access to the Jenkins controller file system to recover the plain text password of that account, likely gaining administrator access to Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50770
- https://github.com/jenkinsci/oic-auth-plugin/issues/259
- https://github.com/jenkins-infra/update-center2/pull/773
- https://github.com/jenkinsci/oic-auth-plugin/pull/287
- https://github.com/jenkinsci/oic-auth-plugin
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-3168
- http://www.openwall.com/lists/oss-security/2023/12/13/4
