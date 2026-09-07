# [M] Jenkins Publish to Bitbucket Plugin vulnerable to CSRF and missing permissions check

## Summary
Severity: Medium
Advisory: GHSA-m244-6mff-p355
CVE: CVE-2025-64149
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-m244-6mff-p355
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:publish-to-bitbucket` — affected >=0

## Details
Jenkins Publish to Bitbucket Plugin 0.4 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to connect to an attacker-specified HTTP URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, this endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64149
- https://github.com/jenkinsci/publish-to-bitbucket-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3576
- http://www.openwall.com/lists/oss-security/2025/10/29/2
