# [M] Missing permission check in Jenkins OpenShift Deployer Plugin

## Summary
Severity: Medium
Advisory: GHSA-78fg-pvgg-6g3r
CVE: CVE-2022-36909
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-78fg-pvgg-6g3r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:openshift-deployer` — affected >=0

## Details
OpenShift Deployer Plugin 1.2.0 and earlier does not perform permission checks in methods implementing form validation.

This allows attackers with Overall/Read permission to check for the existence of an attacker-specified file path on the Jenkins controller file system and to upload a SSH key file from the Jenkins controller file system to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36909
- https://github.com/jenkinsci/openshift-deployer-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-1375%20(2)
- http://www.openwall.com/lists/oss-security/2022/07/27/1
