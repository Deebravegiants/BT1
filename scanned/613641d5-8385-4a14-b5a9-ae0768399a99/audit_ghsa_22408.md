# [H] CSRF vulnerability in Jenkins Shelve Project Plugin

## Summary
Severity: High
Advisory: GHSA-9f37-ggxm-h6wx
CVE: CVE-2020-2321
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9f37-ggxm-h6wx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:shelve-project-plugin` — affected >=0 <3.1

## Details
Jenkins Shelve Project Plugin 3.0 and earlier does not require POST requests for HTTP endpoints, resulting in cross-site request forgery (CSRF) vulnerabilities.

These vulnerabilities allow attackers to shelve, unshelve, or delete a project.

Jenkins Shelve Project Plugin 3.1 requires POST requests for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2321
- https://github.com/jenkinsci/shelve-project-plugin/commit/5cb9a4733e9cf37d2e7932928698537b1a9fdaec
- https://github.com/jenkinsci/shelve-project-plugin
- https://www.jenkins.io/security/advisory/2020-12-03/#SECURITY-2108
- http://www.openwall.com/lists/oss-security/2020/12/03/2
