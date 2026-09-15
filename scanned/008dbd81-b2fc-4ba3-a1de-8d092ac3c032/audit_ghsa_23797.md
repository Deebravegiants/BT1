# [C] Script security sandbox bypass in Jenkins Email Extension Plugin

## Summary
Severity: Critical
Advisory: GHSA-qwm8-vgm6-f86p
CVE: CVE-2019-1003032
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qwm8-vgm6-f86p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <2.65

## Details
A sandbox bypass vulnerability exists in Jenkins Email Extension Plugin 2.64 and earlier in pom.xml, src/main/java/hudson/plugins/emailext/ExtendedEmailPublisher.java, src/main/java/hudson/plugins/emailext/plugins/content/EmailExtScript.java, src/main/java/hudson/plugins/emailext/plugins/content/ScriptContent.java, src/main/java/hudson/plugins/emailext/plugins/trigger/AbstractScriptTrigger.java that allows attackers with Job/Configure permission to execute arbitrary code on the Jenkins master JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003032
- https://github.com/jenkinsci/email-ext-plugin
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-1340
- http://www.securityfocus.com/bid/107476
