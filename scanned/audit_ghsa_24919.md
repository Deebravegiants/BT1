# [H] Improper Privilege Management in Jenkins

## Summary
Severity: High
Advisory: GHSA-p4p5-3v2j-w5rv
CVE: CVE-2018-1000865
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p4p5-3v2j-w5rv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.48

## Details
A sandbox bypass vulnerability exists in Script Security Plugin 1.47 and earlier in groovy-sandbox/src/main/java/org/kohsuke/groovy/sandbox/SandboxTransformer.java that allows attackers with Job/Configure permission to execute arbitrary code on the Jenkins master JVM, if plugins using the Groovy sandbox are installed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000865
- https://github.com/jenkinsci/script-security-plugin/commit/16c862ae9d4038a3edbd8bdfb0fd1401a509d56b
- https://access.redhat.com/errata/RHBA-2019:0326
- https://access.redhat.com/errata/RHBA-2019:0327
- https://jenkins.io/security/advisory/2018-10-29/#SECURITY-1186
