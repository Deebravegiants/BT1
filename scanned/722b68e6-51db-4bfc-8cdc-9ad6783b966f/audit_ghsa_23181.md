# [H] Missing permission checks in Pipeline GitHub Notify Step Plugin allows capturing credentials

## Summary
Severity: High
Advisory: GHSA-x7rc-5mjg-5pvr
CVE: CVE-2020-2117
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x7rc-5mjg-5pvr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-githubnotify-step` — affected >=0 <1.0.5

## Details
A missing permission check in Jenkins Pipeline GitHub Notify Step Plugin 1.0.4 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2117
- https://github.com/jenkinsci/pipeline-githubnotify-step-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-812%20(1)
- http://www.openwall.com/lists/oss-security/2020/02/12/3
