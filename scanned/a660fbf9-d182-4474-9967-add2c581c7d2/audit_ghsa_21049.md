# [M] Jenkins Repository Connector Plugin allows attackers with Overall/Read permission to enumerate credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-76pg-mr9v-5vwc
CVE: CVE-2022-36903
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-76pg-mr9v-5vwc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:repository-connector` — affected >=0

## Details
Jenkins Repository Connector Plugin 2.2.0 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36903
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2665%20%281%29
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2665%20(1)
- http://www.openwall.com/lists/oss-security/2022/07/27/1
