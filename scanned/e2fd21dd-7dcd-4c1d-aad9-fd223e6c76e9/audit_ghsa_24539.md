# [M] Jenkins Dependency Graph Viewer Plugin contains Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-4wj7-rh5h-5qmr
CVE: CVE-2019-10349
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4wj7-rh5h-5qmr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:depgraph-view` — affected >=0 <0.14

## Details
A stored cross site scripting vulnerability in Jenkins Dependency Graph Viewer Plugin 0.13 and earlier allowed attackers able to configure jobs in Jenkins to inject arbitrary HTML and JavaScript in the plugin-provided web pages in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10349
- https://github.com/jenkinsci/depgraph-view-plugin/commit/288496fd2e6fe922da3b43067e73cfac07a910e8
- https://github.com/jenkinsci/depgraph-view-plugin
- https://jenkins.io/security/advisory/2019-07-11/#SECURITY-1177
- http://packetstormsecurity.com/files/153610/Jenkins-Dependency-Graph-View-0.13-Cross-Site-Scripting.html
- http://www.openwall.com/lists/oss-security/2019/07/11/4
- http://www.securityfocus.com/bid/109156
