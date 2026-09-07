# [M] Open redirect vulnerability in Jenkins CAS Plugin

## Summary
Severity: Medium
Advisory: GHSA-2vvr-5757-qp87
CVE: CVE-2021-21673
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2vvr-5757-qp87
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cas-plugin` — affected >=0 <1.6.1

## Details
Jenkins CAS Plugin 1.6.0 and earlier improperly determines that a redirect URL after login is legitimately pointing to Jenkins.

This allows attackers to perform phishing attacks by having users go to a Jenkins URL that will forward them to a different site after successful authentication.

Jenkins CAS Plugin 1.6.1 only redirects to relative (Jenkins) URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21673
- https://github.com/jenkinsci/cas-plugin/commit/8ac536a953156160dbabb61bdb3b9bc75c3d0ef9
- https://github.com/jenkinsci/cas-plugin
- https://www.jenkins.io/security/advisory/2021-06-30/#SECURITY-2387
- http://www.openwall.com/lists/oss-security/2021/06/30/1
