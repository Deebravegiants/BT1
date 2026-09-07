# [H] Cross-site Scripting in Jenkins Application Detector Plugin

## Summary
Severity: High
Advisory: GHSA-6wh8-mr6f-6cx2
CVE: CVE-2022-30960
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-6wh8-mr6f-6cx2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:app-detector` — affected >=0 <1.0.9

## Details
Jenkins Application Detector Plugin 1.0.8 and earlier does not escape the name of Chois Application Version parameters on views displaying parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30960
- https://github.com/jenkinsci/app-detector-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2717
