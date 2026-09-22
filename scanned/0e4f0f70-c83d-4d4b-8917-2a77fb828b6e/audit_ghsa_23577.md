# [M] Password written to the build log by Jenkins SQLPlus Script Runner Plugin

## Summary
Severity: Medium
Advisory: GHSA-rwh3-5g7v-3c5m
CVE: CVE-2020-2312
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rwh3-5g7v-3c5m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sqlplus-script-runner` — affected >=0 <2.0.13

## Details
Jenkins SQLPlus Script Runner Plugin 2.0.12 and earlier prints the `sqlplus` command invocation to the build logs.

This log message does not redact a password provided as part of a command line argument. This password can be viewed by users with Item/Read permission.

Jenkins SQLPlus Script Runner Plugin 2.0.13 no longer prints the password in the build logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2312
- https://github.com/jenkinsci/sqlplus-script-runner-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2129
