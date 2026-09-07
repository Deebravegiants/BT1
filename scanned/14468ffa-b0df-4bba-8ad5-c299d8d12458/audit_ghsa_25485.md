# [M] Reflected XSS vulnerability in Jenkins gitlab-hook Plugin

## Summary
Severity: Medium
Advisory: GHSA-8696-836p-c8qp
CVE: CVE-2020-2096
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8696-836p-c8qp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.ruby-plugins:gitlab-hook` — affected >=0

## Details
Jenkins Gitlab Hook Plugin 1.4.2 and earlier does not escape project names in the `build_now` endpoint, resulting in a reflected XSS vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2096
- https://github.com/jenkinsci/gitlab-hook-plugin
- https://jenkins.io/security/advisory/2020-01-15/#SECURITY-1683
- http://packetstormsecurity.com/files/155967/Jenkins-Gitlab-Hook-1.4.2-Cross-Site-Scripting.html
- http://www.openwall.com/lists/oss-security/2020/01/15/1
