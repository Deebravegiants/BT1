# [M] Jenkins Monitoring Plugin vulnerable to Denial of service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hw83-jpxr-g225
CVE: CVE-2019-1003022
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hw83-jpxr-g225
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:monitoring` — affected >=0 <1.75.0

## Details
A denial of service vulnerability exists in Jenkins Monitoring Plugin 1.74.0 and earlier in PluginImpl.java that allows attackers to kill threads running on the Jenkins master.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003022
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1153
