# [M] CSRF vulnerability in Jenkins OpenShift Deployer Plugin

## Summary
Severity: Medium
Advisory: GHSA-8528-c6m6-gppm
CVE: CVE-2022-36906
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-8528-c6m6-gppm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:openshift-deployer` — affected >=0

## Details
OpenShift Deployer Plugin 1.2.0 and earlier does not perform a permission check in a method implementing form validation.

This form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36906
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-1375%20(1)
- http://www.openwall.com/lists/oss-security/2022/07/27/1
