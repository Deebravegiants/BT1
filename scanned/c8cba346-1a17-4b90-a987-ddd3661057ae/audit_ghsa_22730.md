# [M] Jenkins NeuVector Vulnerability Scanner Plugin stored credentials in plain text 

## Summary
Severity: Medium
Advisory: GHSA-3fpx-g9h3-hh8x
CVE: CVE-2019-10430
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3fpx-g9h3-hh8x
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:neuvector-vulnerability-scanner` — affected >=0 <1.6

## Details
Jenkins NeuVector Vulnerability Scanner Plugin 1.5 and earlier stored credentials unencrypted in its global configuration file on the Jenkins master where they could be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10430
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1504
- http://www.openwall.com/lists/oss-security/2019/09/25/3
