# [H] Bitbucket Server Integration Plugin allows bypassing CSRF protection for any URL

## Summary
Severity: High
Advisory: GHSA-qjw6-xvrm-5f2h
CVE: CVE-2025-24398
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-qjw6-xvrm-5f2h
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:atlassian-bitbucket-server-integration` — affected >=2.1.0 <4.1.4

## Details
An extension point in Jenkins allows selectively disabling cross-site request forgery (CSRF) protection for specific URLs. Bitbucket Server Integration Plugin implements this extension point to support OAuth 1.0 authentication.

In Bitbucket Server Integration Plugin 2.1.0 through 4.1.3 (both inclusive) this implementation is too permissive, allowing attackers to craft URLs that would bypass the CSRF protection of any target URL.

Bitbucket Server Integration Plugin 4.1.4 restricts which URLs it disables cross-site request forgery (CSRF) protection for to the URLs that needs it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24398
- https://github.com/jenkinsci/atlassian-bitbucket-server-integration-plugin
- https://www.jenkins.io/security/advisory/2025-01-22/#SECURITY-3434
