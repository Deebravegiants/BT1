# [H] Improper handling of untrusted branches in Gitea Jenkins Plugin

## Summary
Severity: High
Advisory: GHSA-q98c-rqx7-7ghf
CVE: CVE-2019-10330
CWE: CWE-693, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q98c-rqx7-7ghf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitea` — affected >=0 <1.1.2

## Details
Jenkins Gitea Plugin prior to 1.1.2 did not implement trusted revisions, allowing attackers without commit access to the Git repo to change Jenkinsfiles even if Jenkins is configured to consider them to be untrusted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10330
- https://github.com/jenkinsci/gitea-plugin/commit/7555cb7c168cfa49d31271e7d65d76c1fab311f7
- https://jenkins.io/security/advisory/2019-05-31/#SECURITY-1046
- http://www.openwall.com/lists/oss-security/2019/05/31/2
- http://www.securityfocus.com/bid/108540
