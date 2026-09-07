# [M] Cross-site Scripting in Jenkins Active Choices plugin

## Summary
Severity: Medium
Advisory: GHSA-c2hw-w9qm-q5r9
CVE: CVE-2017-1000386
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c2hw-w9qm-q5r9
Type: github-advisory

## Affected
- Maven: `org.biouno:uno-choice` — affected >=0 <2.0

## Details
Jenkins Active Choices plugin version 1.5.3 and earlier allowed users with Job/Configure permission to provide arbitrary HTML to be shown on the 'Build With Parameters' page through the 'Active Choices Reactive Reference Parameter' type. This could include, for example, arbitrary JavaScript. Active Choices now sanitizes the HTML inserted on the 'Build With Parameters' page if and only if the script is executed in a sandbox. As unsandboxed scripts are subject to administrator approval, it is up to the administrator to allow or disallow problematic script output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000386
- https://jenkins.io/security/advisory/2017-10-23
- http://www.securityfocus.com/bid/101538
