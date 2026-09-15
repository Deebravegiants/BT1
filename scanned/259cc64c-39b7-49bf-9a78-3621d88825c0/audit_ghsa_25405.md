# [C] Script security sandbox bypass in Jenkins Job DSL Plugin

## Summary
Severity: Critical
Advisory: GHSA-5r74-pgmq-92mm
CVE: CVE-2019-1003034
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5r74-pgmq-92mm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:job-dsl` — affected >=0 <1.72

## Details
A sandbox bypass vulnerability exists in Jenkins Job DSL Plugin 1.71 and earlier in job-dsl-core/src/main/groovy/javaposse/jobdsl/dsl/AbstractDslScriptLoader.groovy, job-dsl-plugin/build.gradle, job-dsl-plugin/src/main/groovy/javaposse/jobdsl/plugin/JobDslWhitelist.groovy, job-dsl-plugin/src/main/groovy/javaposse/jobdsl/plugin/SandboxDslScriptLoader.groovy that allows attackers with control over Job DSL definitions to execute arbitrary code on the Jenkins master JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003034
- https://github.com/jenkinsci/job-dsl-plugin/commit/a2dc2def098cd6e91df0981fdf838fb44a991496
- https://access.redhat.com/errata/RHSA-2019:0739
- https://github.com/jenkinsci/job-dsl-plugin
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-1342
- http://www.securityfocus.com/bid/107476
