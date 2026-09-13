# [H] Cross-site WebSocket hijacking vulnerability in the Jenkins CLI

## Summary
Severity: High
Advisory: GHSA-53ph-2r2x-vqw8
CVE: CVE-2024-23898
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-53ph-2r2x-vqw8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.217 <2.426.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.427 <2.442
- Maven: `org.jenkins-ci.main:jenkins-core` — affected 2.441

## Details
Jenkins has a built-in command line interface (CLI) to access Jenkins from a script or shell environment. Since Jenkins 2.217 and LTS 2.222.1, one of the ways to communicate with the CLI is through a WebSocket endpoint. This endpoint relies on the default Jenkins web request authentication functionality, like HTTP Basic authentication with API tokens, or session cookies. This endpoint is enabled when running on a version of Jetty for which Jenkins supports WebSockets. This is the case when using the provided native installers, packages, or the Docker containers, as well as when running Jenkins with the command java -jar jenkins.war.

Jenkins 2.217 through 2.441 (both inclusive), LTS 2.222.1 through 2.426.2 (both inclusive) does not perform origin validation of requests made through the CLI WebSocket endpoint, resulting in a cross-site WebSocket hijacking (CSWSH) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23898
- https://github.com/jenkinsci/jenkins/commit/de450967f38398169650b55c002f1229a3fcdb1b
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3315
- https://www.sonarsource.com/blog/excessive-expansion-uncovering-critical-security-vulnerabilities-in-jenkins
- http://www.openwall.com/lists/oss-security/2024/01/24/6
