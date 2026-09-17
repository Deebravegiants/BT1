# [M] Jenkins lambdatest-automation Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-vw64-g7c6-mm7g
CVE: CVE-2023-46652
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-vw64-g7c6-mm7g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:lambdatest-automation` — affected >=0 <1.20.10

## Details
Jenkins lambdatest-automation Plugin 1.20.9 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate credentials IDs of LAMBDATEST credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in lambdatest-automation Plugin 1.20.10 requires Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46652
- https://github.com/jenkinsci/lambdatest-automation-plugin
- https://www.jenkins.io/security/advisory/2023-10-25/#SECURITY-3222
- http://www.openwall.com/lists/oss-security/2023/10/25/2
