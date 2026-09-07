# [H] Stored XSS vulnerability in Jenkins Pipeline: Supporting APIs Plugin

## Summary
Severity: High
Advisory: GHSA-64r9-x74q-wxmh
CVE: CVE-2022-43409
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-64r9-x74q-wxmh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-support` — affected >=0 <839.v35e2736cfd5c

## Details
Pipeline: Supporting APIs Plugin provides a feature to add hyperlinks, that send POST requests when clicked, to build logs. These links are used by Pipeline: Input Step Plugin to allow users to proceed or abort the build, or by Pipeline: Job Plugin to allow users to forcibly terminate the build after aborting it.

Pipeline: Supporting APIs Plugin 838.va_3a_087b_4055b and earlier does not sanitize or properly encode URLs of these hyperlinks in build logs.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to create Pipelines.

Pipeline: Supporting APIs Plugin 839.v35e2736cfd5c properly encodes URLs of these hyperlinks in build logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43409
- https://github.com/jenkinsci/workflow-support-plugin/commit/35e2736cfd5c56799eece176328906d92b6a0dd1
- https://github.com/jenkinsci/workflow-support-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2881
- http://www.openwall.com/lists/oss-security/2022/10/19/3
