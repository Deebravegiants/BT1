# [M] SSL/TLS certificate validation unconditionally disabled by Jenkins Micro Focus Application Automation Tools Plugin

## Summary
Severity: Medium
Advisory: GHSA-q296-9j5x-fxf4
CVE: CVE-2021-22511
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q296-9j5x-fxf4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:hp-application-automation-tools-plugin` — affected >=0 <6.8

## Details
Micro Focus Application Automation Tools Plugin 6.7 and earlier unconditionally disables SSL/TLS certificate validation for connections to Service Virtualization servers.

Micro Focus Application Automation Tools Plugin 6.8 no longer disables SSL/TLS certificate validation unconditionally by default. It provides an option to disable SSL/TLS certification validation for connections to Service Virtualization servers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22511
- https://github.com/jenkinsci/hpe-application-automation-tools-plugin/commit/b286378aa22bc48ed77d259200cb6863a532c2df
- https://github.com/jenkinsci/hpe-application-automation-tools-plugin
- https://www.jenkins.io/security/advisory/2021-04-07/#SECURITY-2176
