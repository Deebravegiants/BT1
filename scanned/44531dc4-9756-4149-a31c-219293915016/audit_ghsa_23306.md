# [H] Protection Mechanism Failure in Jenkins Script Security Plugin

## Summary
Severity: High
Advisory: GHSA-784j-h234-m56x
CVE: CVE-2019-1003000
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-784j-h234-m56x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.50

## Details
A sandbox bypass vulnerability exists in Script Security Plugin 1.49 and earlier in src/main/java/org/jenkinsci/plugins/scriptsecurity/sandbox/groovy/GroovySandbox.java that allows attackers with the ability to provide sandboxed scripts to execute arbitrary code on the Jenkins master JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003000
- https://github.com/jenkinsci/script-security-plugin/commit/2c5122e50742dd16492f9424992deb21cc07837c
- https://access.redhat.com/errata/RHBA-2019:0326
- https://access.redhat.com/errata/RHBA-2019:0327
- https://jenkins.io/security/advisory/2019-01-08/#SECURITY-1266
- https://www.exploit-db.com/exploits/46453
- https://www.exploit-db.com/exploits/46572
- http://packetstormsecurity.com/files/152132/Jenkins-ACL-Bypass-Metaprogramming-Remote-Code-Execution.html
- http://www.rapid7.com/db/modules/exploit/multi/http/jenkins_metaprogramming
