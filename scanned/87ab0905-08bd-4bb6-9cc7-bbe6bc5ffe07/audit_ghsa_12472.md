# [M] Open redirect vulnerability in Jenkins OpenId Connect Authentication Plugin 

## Summary
Severity: Medium
Advisory: GHSA-9qv8-7jfq-73j2
CVE: CVE-2023-50771
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-9qv8-7jfq-73j2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:oic-auth` — affected >=0 <3.0

## Details
Jenkins OpenId Connect Authentication Plugin 2.6 and earlier improperly determines that a redirect URL after login is legitimately pointing to Jenkins, allowing attackers to perform phishing attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50771
- https://github.com/jenkins-infra/update-center2/pull/767
- https://github.com/jenkinsci/oic-auth-plugin/pull/261
- https://github.com/jenkinsci/oic-auth-plugin/commit/a97a4041f39c85aa746c047ac14ee69199dadf05
- https://github.com/jenkinsci/oic-auth-plugin
- https://github.com/jenkinsci/oic-auth-plugin/releases/tag/oic-auth-3.0
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-2979
- http://www.openwall.com/lists/oss-security/2023/12/13/4
