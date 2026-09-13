# [H] RCE vulnerability in Jenkins DotCi Plugin

## Summary
Severity: High
Advisory: GHSA-x3jj-rgw9-7r5g
CVE: CVE-2022-41237
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-x3jj-rgw9-7r5g
Type: github-advisory

## Affected
- Maven: `com.groupon.jenkins-ci.plugins:DotCi` — affected >=0

## Details
DotCi Plugin 2.40.00 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types.

This results in a remote code execution (RCE) vulnerability exploitable by attackers able to modify `.ci.yml` files in SCM. This plugin has been suspended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41237
- https://github.com/jenkinsci/DotCi
- https://plugins.jenkins.io/DotCi
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-1737
- https://www.jenkins.io/security/plugins/#suspensions
