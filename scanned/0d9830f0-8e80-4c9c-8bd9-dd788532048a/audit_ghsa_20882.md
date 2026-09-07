# [M] Lack of authentication mechanism in Jenkins DotCi Plugin webhook

## Summary
Severity: Medium
Advisory: GHSA-9mc6-vgmq-x6xf
CVE: CVE-2022-41238
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-9mc6-vgmq-x6xf
Type: github-advisory

## Affected
- Maven: `com.groupon.jenkins-ci.plugins:DotCi` — affected >=0

## Details
DotCi Plugin provides a webhook endpoint at `/githook/` that can be used to trigger builds of the job for a GitHub repository.

In DotCi Plugin 2.40.00 and earlier, this endpoint can be accessed without authentication.

This allows unauthenticated attackers to trigger builds of jobs corresponding to the attacker-specified repository for attacker-specified commits.

This plugin has been suspended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41238
- https://github.com/jenkinsci/DotCi
- https://plugins.jenkins.io/DotCi
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2867
- https://www.jenkins.io/security/plugins/#suspensions
