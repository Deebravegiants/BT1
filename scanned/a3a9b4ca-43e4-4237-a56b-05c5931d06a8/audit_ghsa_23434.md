# [M] Users with Overall/Read access can enumerate credentials IDs in Amazon EC2 Plugin

## Summary
Severity: Medium
Advisory: GHSA-rmp9-mc8w-mqf3
CVE: CVE-2020-2188
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rmp9-mc8w-mqf3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ec2` — affected >=0 <1.50.2

## Details
Amazon EC2 Plugin provides a list of applicable credentials IDs to allow users configuring the plugin to select the one to use.

This functionality does not correctly check permissions in Amazon EC2 Plugin 1.50.1 and earlier, allowing any user with Overall/Read permission to get a list of valid credentials IDs. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in Amazon EC2 Plugin 1.50.2 now requires Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2188
- https://github.com/jenkinsci/ec2-plugin
- https://jenkins.io/security/advisory/2020-05-06/#SECURITY-1844
- http://www.openwall.com/lists/oss-security/2020/05/06/3
