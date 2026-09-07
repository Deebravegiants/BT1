# [M] Jenkins CRX Content Package Deployer Plugin subject to credentials enumeration via Missing Authorization

## Summary
Severity: Medium
Advisory: GHSA-4cmq-88f8-53r5
CVE: CVE-2019-10439
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4cmq-88f8-53r5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:crx-content-package-deployer` — affected >=0 <1.9

## Details
A missing permission check in Jenkins CRX Content Package Deployer Plugin prior to version 1.9 in various 'doFillCredentialsIdItems' methods allowed users with Overall/Read access to enumerate credentials ID of credentials stored in Jenkins. This issue is patched in version 1.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10439
- https://github.com/jenkinsci/crx-content-package-deployer-plugin/commit/06cd0e7e1b3f2fb87b3fa332ee1da710ca94b8e1
- https://github.com/jenkinsci/crx-content-package-deployer-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1006%20(2)
