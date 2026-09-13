# [M] Jenkins Credentials Binding Plugin Stores Passwords in a Recoverable Format

## Summary
Severity: Medium
Advisory: GHSA-j7gw-mwfg-vqf4
CVE: CVE-2019-1010241
CWE: CWE-257, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j7gw-mwfg-vqf4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials-binding` — affected 1.17

## Details
Jenkins Credentials Binding Plugin Jenkins 1.17 is affected by: CWE-257: Storing Passwords in a Recoverable Format. The impact is: Authenticated users can recover credentials. The component is: config-variables.jelly line #30 (passwordVariable). The attack vector is: Attacker creates and executes a Jenkins job.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010241
- https://docs.google.com/document/d/1MBEoJSMvkjp5Kua0bRD_kiDBisL0fOCwTL9uMWj4lGA/edit?usp=sharing
- https://github.com/jenkinsci/credentials-binding-plugin
- https://web.archive.org/web/20200227030005/https://www.securityfocus.com/bid/109320
