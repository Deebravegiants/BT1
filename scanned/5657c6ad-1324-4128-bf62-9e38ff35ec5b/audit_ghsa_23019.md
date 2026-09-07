# [M] Stored XSS vulnerability in Jenkins FitNesse Plugin

## Summary
Severity: Medium
Advisory: GHSA-f6vx-3fq6-hxm8
CVE: CVE-2020-2175
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f6vx-3fq6-hxm8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fitnesse` — affected >=0 <1.32

## Details
Jenkins FitNesse Plugin 1.31 and earlier does not correctly escape report contents before showing them on the Jenkins UI.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by users able to control the XML input files processed by the plugin.

Jenkins FitNesse Plugin 1.32 escapes content from XML input files before rendering it on the Jenkins UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2175
- https://github.com/jenkinsci/fitnesse-plugin/commit/309d40212338ad6e388f61892e4386f6645438a9
- https://github.com/jenkinsci/fitnesse-plugin/commit/a49167115cc0a3dfca1c139c2c277a7c5c06074d
- https://github.com/jenkinsci/fitnesse-plugin/commit/db72cc49b5cb8a33359805a86a841851673def2d
- https://github.com/jenkinsci/fitnesse-plugin
- https://jenkins.io/security/advisory/2020-04-07/#SECURITY-1801
- http://www.openwall.com/lists/oss-security/2020/04/07/3
