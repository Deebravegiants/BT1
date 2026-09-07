# [H] Stored XSS vulnerability in Jenkins console links

## Summary
Severity: High
Advisory: GHSA-gfhj-524q-gcrm
CVE: CVE-2020-2223
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gfhj-524q-gcrm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.235.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.236 <2.245

## Details
Jenkins 2.244 and earlier, LTS 2.235.1 and earlier does not escape the `href` attribute of links to downstream jobs displayed in the build console page. This results in a stored cross-site scripting (XSS) vulnerability exploitable by users with Job/Configure permission.

Jenkins 2.245, LTS 2.235.2 escapes the `href` attribute of these links.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2223
- https://github.com/jenkinsci/jenkins/commit/11f4a351224ef04cfeb9c7636fb1590b67543f3c
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-07-15/#SECURITY-1945
- http://www.openwall.com/lists/oss-security/2020/07/15/5
