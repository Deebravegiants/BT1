# [M] Persisted XSS Vulnerability in Jenkins Sidebar Link Plugin

## Summary
Severity: Medium
Advisory: GHSA-477r-v22q-r42f
CVE: CVE-2017-1000088
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-477r-v22q-r42f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sidebar-link` — affected >=0 <1.9

## Details
The Sidebar Link plugin allows users able to configure jobs, views, and agents to add entries to the sidebar of these objects. There was no input validation, which meant users were able to use javascript: schemes for these links.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000088
- https://jenkins.io/security/advisory/2017-07-10
