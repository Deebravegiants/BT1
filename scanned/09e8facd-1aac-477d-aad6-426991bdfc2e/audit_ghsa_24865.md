# [M] Incorrect Authorization in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-7r4h-2h23-6jq9
CVE: CVE-2017-2599
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7r4h-2h23-6jq9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.32.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.34 <2.44

## Details
Jenkins before versions 2.44 and 2.32.2 is vulnerable to an insufficient permission check. This allows users with permissions to create new items (e.g. jobs) to overwrite existing items they don't have access to (SECURITY-321).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2599
- https://github.com/jenkinsci/jenkins/commit/4ed5c850b6855ab064a66d02fb338f366853ce89
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2599
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-02-01
