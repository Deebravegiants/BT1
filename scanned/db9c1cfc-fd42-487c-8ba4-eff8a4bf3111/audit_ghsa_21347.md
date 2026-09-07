# [H] Stored XSS vulnerability in Jenkins Contrast Continuous Application Security Plugin

## Summary
Severity: High
Advisory: GHSA-hvcr-927w-qcvq
CVE: CVE-2022-43420
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-hvcr-927w-qcvq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:contrast-continuous-application-security` — affected >=0 <3.10

## Details
Contrast Continuous Application Security Plugin 3.9 and earlier does not escape data returned from the Contrast service when generating a report.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control or modify Contrast service API responses.

Contrast Continuous Application Security Plugin 3.10 escapes the affected data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43420
- https://github.com/jenkinsci/contrast-continuous-application-security-plugin/commit/1babcd1e972a265527af12a9f85393d08937859c
- https://github.com/jenkinsci/contrast-continuous-application-security-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2836
- http://www.openwall.com/lists/oss-security/2022/10/19/3
