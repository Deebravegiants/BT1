# [C] CVE-2019-1003030

## Summary
Severity: Critical
Advisory: CVE-2019-1003030
Aliases: GHSA-r6mc-mrvr-23cr
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/CVE-2019-1003030
Type: osv

## Details
A sandbox bypass vulnerability exists in Jenkins Pipeline: Groovy Plugin 2.63 and earlier in pom.xml, src/main/java/org/jenkinsci/plugins/workflow/cps/CpsGroovyShell.java that allows attackers able to control pipeline scripts to execute arbitrary code on the Jenkins master JVM.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-1003030
- http://www.securityfocus.com/bid/107476
- https://access.redhat.com/errata/RHSA-2019:0739
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-1336%20%282%29
- http://packetstormsecurity.com/files/159603/Jenkins-2.63-Sandbox-Bypass.html
