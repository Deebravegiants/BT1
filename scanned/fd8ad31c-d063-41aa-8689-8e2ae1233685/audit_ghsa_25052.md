# [M] Missing permission checks in Health Advisor by CloudBees Plugin

## Summary
Severity: Medium
Advisory: GHSA-h72v-652w-xv64
CVE: CVE-2020-2094
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h72v-652w-xv64
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloudbees-jenkins-advisor` — affected >=0 <3.0.1

## Details
Health Advisor by CloudBees Plugin 3.0 and earlier does not perform permission checks in methods performing form validation. This allows users with Overall/Read access to send an email with fixed content to an attacker-specified recipient.

Additionally, these form validation methods do not require POST requests, resulting in a CSRF vulnerability.

Health Advisor by CloudBees Plugin 3.0.1 requires POST requests and Overall/Administer permission for the affected form validation methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2094
- https://github.com/jenkinsci/cloudbees-jenkins-advisor-plugin/commit/f53fe8a41a1566fdd7d2996779f6c5684ef3e2df
- https://github.com/jenkinsci/cloudbees-jenkins-advisor-plugin
- https://jenkins.io/security/advisory/2020-01-15/#SECURITY-1708
