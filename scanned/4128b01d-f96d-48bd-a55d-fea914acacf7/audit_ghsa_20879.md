# [H] Stored XSS vulnerability in Jenkins Walti plugin

## Summary
Severity: High
Advisory: GHSA-7qpm-vmwv-hq7h
CVE: CVE-2022-41240
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-7qpm-vmwv-hq7h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:walti` — affected >=0

## Details
Jenkins Walti Plugin 1.0.1 and earlier does not escape the information provided by the Walti API, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to provide malicious API responses from Walti.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41240
- https://github.com/jenkins-infra/update-center2/pull/644
- https://github.com/jenkinsci/walti-plugin
- https://plugins.jenkins.io/walti
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-1870
