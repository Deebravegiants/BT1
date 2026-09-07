# [M] CSRF vulnerability in Jenkins Subversion Plugin

## Summary
Severity: Medium
Advisory: GHSA-m5cw-c64p-77h6
CVE: CVE-2022-29048
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-m5cw-c64p-77h6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:subversion` — affected >=0 <2.15.4

## Details
Subversion Plugin 2.15.3 and earlier does not require POST requests for several form validation methods, resulting in cross-site request forgery (CSRF) vulnerabilities.

These vulnerabilities allow attackers to connect to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29048
- https://github.com/jenkinsci/subversion-plugin/commit/882a7d359f6ac73c53d787bff4d62eba837001ea
- https://github.com/jenkinsci/subversion-plugin
- https://support.apple.com/kb/HT213345
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2075
- http://seclists.org/fulldisclosure/2022/Jul/18
