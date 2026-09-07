# [M] Jenkins Git client Plugin file system information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g2pq-9jr7-w6gv
CVE: CVE-2025-58458
CWE: CWE-200, CWE-538
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-g2pq-9jr7-w6gv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git-client` — affected >=0 <6.3.3

## Details
In Jenkins Git client Plugin 6.3.2 and earlier, Git URL field form validation responses differ based on whether the specified file path exists on the controller when specifying `amazon-s3` protocol for use with JGit, allowing attackers with Overall/Read permission to check for the existence of an attacker-specified file path on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-58458
- https://github.com/jenkinsci/git-client-plugin/commit/20090a86c3ebc72e5283c882de73e3a4459137bb
- https://github.com/jenkinsci/git-client-plugin
- https://www.jenkins.io/security/advisory/2025-09-03/#SECURITY-3590
- http://www.openwall.com/lists/oss-security/2025/09/03/4
