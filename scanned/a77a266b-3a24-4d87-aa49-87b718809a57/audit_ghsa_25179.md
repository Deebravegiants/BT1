# [H] CSRF vulnerability in Pipeline GitHub Notify Step Plugin allows capturing credentials

## Summary
Severity: High
Advisory: GHSA-qhxf-m7jm-jc57
CVE: CVE-2020-2116
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qhxf-m7jm-jc57
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-githubnotify-step` — affected >=0 <1.0.5

## Details
A cross-site request forgery vulnerability in Jenkins Pipeline GitHub Notify Step Plugin 1.0.4 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2116
- https://github.com/jenkinsci/pipeline-githubnotify-step-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-812%20(1)
- http://www.openwall.com/lists/oss-security/2020/02/12/3
