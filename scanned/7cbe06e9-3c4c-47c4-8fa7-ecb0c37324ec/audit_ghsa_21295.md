# [M] Jenkins Job Import Plugin allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-4g29-r7vj-2rpv
CVE: CVE-2022-43413
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-4g29-r7vj-2rpv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:job-import-plugin` — affected >=0 <3.6

## Details
Jenkins Job Import Plugin 3.5 and earlier does not perform a permission check in an HTTP endpoint, allowing attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. An enumeration of credentials IDs in Job Import Plugin 3.6 requires Job Import/Import Jobs permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43413
- https://github.com/jenkinsci/job-import-plugin/commit/1b4119849571d4879977c529f9972d271ad6a630
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2791
- http://www.openwall.com/lists/oss-security/2022/10/19/3
