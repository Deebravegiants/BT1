# [M] Jenkins CloudFormation Plugin stores credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-xjrr-5jpv-v6mw
CVE: CVE-2019-1003061
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xjrr-5jpv-v6mw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jenkins-cloudformation-plugin` — affected >=0

## Details
Jenkins CloudFormation Plugin stores credentials unencrypted in job `config.xml` files on the Jenkins controller. These credentials can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

A fix was released for this issue https://github.com/jenkinsci/jenkins-cloudformation-plugin/commit/d492eccee09e9a9202648bd24440814d3226b0f5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003061
- https://github.com/jenkinsci/jenkins-cloudformation-plugin/commit/d492eccee09e9a9202648bd24440814d3226b0f5
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1042
- http://www.openwall.com/lists/oss-security/2019/04/12/2
