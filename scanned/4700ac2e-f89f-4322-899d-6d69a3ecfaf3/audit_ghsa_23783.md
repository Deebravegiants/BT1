# [M] Jenkins Credentials Binding Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-38xm-xhvj-q2qf
CVE: CVE-2018-1000057
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-38xm-xhvj-q2qf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials-binding` — affected >=0 <1.15

## Details
Jenkins Credentials Binding plugin allows specifying passwords and other secrets as environment variables, and will hide them from console output in builds.

However, since Jenkins will try to resolve references to other environment variables in environment variables passed to a build, this can result in values other than the one specified being provided to a build. For example, the value `p4$$w0rd` would result in Jenkins passing on `p4$w0rd`, as `$$` is the escape sequence for a single `$`.

Credentials Binding plugin does not prevent such a transformed value (e.g. `p4$w0rd`) from being shown on the build log, allowing users to reconstruct the actual password value from the transformed one.

Credentials Binding plugin will now escape any `$` characters in password values so they are correctly passed to the build.

This issue did apply to freestyle and other classic job types, but does not apply to Pipelines.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000057
- https://github.com/jenkinsci/credentials-binding-plugin/commit/0c75238933365aa52b26b7c73fd1f742bfaca9b1
- https://github.com/jenkinsci/credentials-binding-plugin
- https://jenkins.io/security/advisory/2018-02-05
