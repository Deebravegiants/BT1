# [M] Jenkins Google Compute Engine Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v98h-rv7j-hf6j
CVE: CVE-2019-16547
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v98h-rv7j-hf6j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-compute-engine` — affected >=0 <4.2.0

## Details
Missing permission checks in various API endpoints in Jenkins Google Compute Engine Plugin 4.1.1 and earlier allow attackers with Overall/Read permission to obtain limited information about the plugin configuration and environment. Google Compute Engine Plugin 4.2.0 requires the appropriate Job/Configure permission to view these metadata.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16547
- https://jenkins.io/security/advisory/2019-11-21/#SECURITY-1585
- http://www.openwall.com/lists/oss-security/2019/11/21/1
