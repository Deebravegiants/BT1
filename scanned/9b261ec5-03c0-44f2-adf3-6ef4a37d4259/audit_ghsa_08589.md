# [M] Jenkins Job Import Plugin does not perform a permission check in an HTTP endpoint

## Summary
Severity: Medium
Advisory: GHSA-p8jh-4p5p-2rfp
CVE: CVE-2026-48926
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-p8jh-4p5p-2rfp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:job-import-plugin` — affected >=0 <143.145.v48f9a

## Details
Jenkins Job Import Plugin 143.v044a_2e819b_27 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in Job Import Plugin 143.145.v48f9a_a_6ff384 requires Job Import/Import Jobs permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48926
- https://github.com/jenkinsci/job-import-plugin
- https://www.jenkins.io/security/advisory/2026-05-27/#SECURITY-3783
