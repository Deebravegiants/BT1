# [H] Jenkins: Stored XSS vulnerability in node offline cause description 

## Summary
Severity: High
Advisory: GHSA-93qh-vwrm-c5pw
CVE: CVE-2026-53441
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-93qh-vwrm-c5pw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.483 <2.568

## Details
Jenkins 2.483 through 2.567 (both inclusive), LTS 2.492.1 through 2.555.2 (both inclusive) does not escape the user-provided description of a generic offline cause that could be set through the `POST config.xml` API, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Agent/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53441
- https://github.com/jenkinsci/jenkins/commit/20041e8090d3b228d586169141ea7f12ffe4444d
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2026-06-10/#SECURITY-3731
