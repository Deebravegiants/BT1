# [H] Jenkins Pipeline: Input Step Plugin

## Summary
Severity: High
Advisory: GHSA-hxpw-7x95-q38m
CVE: CVE-2017-1000108
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hxpw-7x95-q38m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-input-step` — affected >=0 <2.7

## Details
The Pipeline: Input Step Plugin by default allowed users with Item/Read access to a pipeline to interact with the step to provide input. This has been changed, and now requires users to have the Item/Build permission instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000108
- https://github.com/jenkinsci/pipeline-input-step-plugin
- https://jenkins.io/security/advisory/2017-08-07
