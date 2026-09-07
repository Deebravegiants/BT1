# [M] Cross site scripting in Jenkins Mission Control Plugin

## Summary
Severity: Medium
Advisory: GHSA-9523-474x-5h36
CVE: CVE-2019-16563
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9523-474x-5h36
Type: github-advisory

## Affected
- Maven: `tech.andrey.jenkins:mission-control-view` — affected >=0

## Details
Jenkins Mission Control Plugin 0.9.16 and earlier does not escape job display names and build names shown on its view, resulting in a stored XSS vulnerability exploitable by attackers able to change these properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16563
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1592
- http://www.openwall.com/lists/oss-security/2019/12/17/1
