# [M] Jenkins Deployer Framework Plugin allows attackers with Item/Read permission to read deployment logs

## Summary
Severity: Medium
Advisory: GHSA-rqqx-fvqx-539g
CVE: CVE-2022-36891
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-rqqx-fvqx-539g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:deployer-framework` — affected >=0 <86.v7b_a_4a_55b_f3ec

## Details
Jenkins Deployer Framework Plugin 85.v1d1888e8c021 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Item/Read permission to read deployment logs.

Deployer Framework Plugin 86.v7b_a_4a_55b_f3ec requires Deploy Now/Deploy permission to read deployment logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36891
- https://github.com/jenkinsci/deployer-framework-plugin/commit/7ba4a55bf3ec567ee5325ea7b24b4086ac1cb3ad
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2205
- http://www.openwall.com/lists/oss-security/2022/07/27/1
