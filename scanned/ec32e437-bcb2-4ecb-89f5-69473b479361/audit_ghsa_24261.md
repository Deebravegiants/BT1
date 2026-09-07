# [H] Stored XSS vulnerability in Jenkins upstream cause

## Summary
Severity: High
Advisory: GHSA-g4j6-m3m3-crw8
CVE: CVE-2020-2221
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g4j6-m3m3-crw8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.235.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.236 <2.245

## Details
Jenkins 2.244 and earlier, LTS 2.235.1 and earlier does not escape the upstream job's display name shown as part of a build cause, resulting in a stored cross-site scripting vulnerability.

Jenkins 2.245, LTS 2.235.2 escapes the job display name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2221
- https://github.com/jenkinsci/jenkins/commit/f6e575381bdba85afaf27c529d7298091f226e49
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-07-15/#SECURITY-1901
- http://www.openwall.com/lists/oss-security/2020/07/15/5
