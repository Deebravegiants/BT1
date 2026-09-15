# [H] Liquibase Runner Plugin allows users to load arbitrary Java code into controller JVM 

## Summary
Severity: High
Advisory: GHSA-3hvc-xwjp-xr8m
CVE: CVE-2018-1000146
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3hvc-xwjp-xr8m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:liquibase-runner` — affected >=0 <1.4.3

## Details
An arbitrary code execution vulnerability exists in Liquibase Runner Plugin version 1.3.0 and older that allows an attacker with permission to configure jobs to load and execute arbitrary code on the Jenkins master JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000146
- https://github.com/jenkinsci/liquibase-runner-plugin/commit/1817af0b5bb17e690d89c0a1623de8bd47f8c1a1
- https://github.com/jenkinsci/liquibase-runner-plugin/commit/382a1ea84910db28a88089306b24d1e80818f0a5
- https://github.com/jenkinsci/liquibase-runner-plugin/commit/7726ce4569a287e32fbda6f01ad2846ada909436
- https://github.com/jenkinsci/liquibase-runner-plugin
- https://jenkins.io/security/advisory/2018-03-26/#SECURITY-519
