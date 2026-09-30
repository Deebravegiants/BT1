# [H] Sandbox Bypass in Script Security Plugin

## Summary
Severity: High
Advisory: GHSA-x5jm-rj37-5qh7
CVE: CVE-2019-1003005
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x5jm-rj37-5qh7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.51

## Details
A sandbox bypass vulnerability exists in Jenkins Script Security Plugin 1.50 and earlier in src/main/java/org/jenkinsci/plugins/scriptsecurity/sandbox/groovy/SecureGroovyScript.java that allows attackers with Overall/Read permission to provide a Groovy script to an HTTP endpoint that can result in arbitrary code execution on the Jenkins master JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003005
- https://github.com/jenkinsci/script-security-plugin/commit/35119273101af26792457ec177f34f6f4fa49d99
- https://access.redhat.com/errata/RHSA-2019:0739
- https://github.com/jenkinsci/script-security-plugin
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1292
- http://packetstormsecurity.com/files/166778/Jenkins-Remote-Code-Execution.html
