# [M] Jenkins Tag Profiler Plugin vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-49f2-j3pp-22jm
CVE: CVE-2023-33003
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-49f2-j3pp-22jm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:tag-profiler` — affected >=0

## Details
Jenkins Tag Profiler Plugin 0.2 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to reset profiler statistics.

Additionally, this HTTP endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33003
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3083
