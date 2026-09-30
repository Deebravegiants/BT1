# [M] Jenkins Multijob plugin did not check permissions in the Resume Build action

## Summary
Severity: Medium
Advisory: GHSA-p9r2-gghq-hc57
CVE: CVE-2017-1000390
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p9r2-gghq-hc57
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jenkins-multijob-plugin` — affected >=0 <1.26

## Details
Jenkins Multijob plugin version 1.25 and earlier did not check permissions in the Resume Build action, allowing anyone with Job/Read permission to resume the build. Multijob plugin 1.26 introduced a permission check requiring Overall/Administer. This was lowered to Job/Build in version 1.27.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000390
- https://jenkins.io/security/advisory/2017-10-23
- http://www.securityfocus.com/bid/102824
