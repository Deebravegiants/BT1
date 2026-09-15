# [M] Jenkins Deployer Framework Plugin does not restrict application path of applications when configuring a deployment

## Summary
Severity: Medium
Advisory: GHSA-j5qq-6rpm-qjgh
CVE: CVE-2022-36889
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-j5qq-6rpm-qjgh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:deployer-framework` — affected >=0 <86.v7b_a_4a_55b_f3ec

## Details
Jenkins Deployer Framework Plugin 85.v1d1888e8c021 and earlier does not restrict the application path of the applications when configuring a deployment, allowing attackers with Item/Configure permission to upload arbitrary files from the Jenkins controller file system to the selected service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36889
- https://github.com/jenkinsci/deployer-framework-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2764
- http://www.openwall.com/lists/oss-security/2022/07/27/1
