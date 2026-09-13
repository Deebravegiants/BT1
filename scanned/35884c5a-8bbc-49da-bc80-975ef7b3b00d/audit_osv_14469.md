# [C] CVE-2019-1003029

## Summary
Severity: Critical
Advisory: CVE-2019-1003029
Aliases: GHSA-xvxq-hq48-xphm
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/CVE-2019-1003029
Type: osv

## Details
A sandbox bypass vulnerability exists in Jenkins Script Security Plugin 1.53 and earlier in src/main/java/org/jenkinsci/plugins/scriptsecurity/sandbox/groovy/GroovySandbox.java, src/main/java/org/jenkinsci/plugins/scriptsecurity/sandbox/groovy/SecureGroovyScript.java that allows attackers with Overall/Read permission to execute arbitrary code on the Jenkins master JVM.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-1003029
- http://packetstormsecurity.com/files/166778/Jenkins-Remote-Code-Execution.html
- http://www.securityfocus.com/bid/107476
- https://access.redhat.com/errata/RHSA-2019:0739
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-1336%20%281%29
