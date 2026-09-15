# [C] Sandbox escape in Jenkins Email Extension Plugin

## Summary
Severity: Critical
Advisory: GHSA-c9c2-wcxh-3w5j
CVE: CVE-2023-25765
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-c9c2-wcxh-3w5j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <2.94

## Details
In Jenkins Email Extension Plugin 2.93 and earlier, templates defined inside a folder were not subject to Script Security protection, allowing attackers able to define email templates in folders to bypass the sandbox protection and execute arbitrary code in the context of the Jenkins controller JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25765
- https://github.com/jenkinsci/email-ext-plugin/commit/ffe44a4c1c1830325787d7ef5e9e19ebf9a936f9
- https://github.com/jenkinsci/email-ext-plugin
- https://www.jenkins.io/security/advisory/2023-02-15/#SECURITY-2939
- http://www.openwall.com/lists/oss-security/2023/02/15/4
