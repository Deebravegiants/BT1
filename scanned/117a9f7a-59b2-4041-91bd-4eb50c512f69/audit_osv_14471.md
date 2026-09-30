# [H] CVE-2019-1003033

## Summary
Severity: High
Advisory: CVE-2019-1003033
Aliases: GHSA-fm3j-r98g-97jh
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/CVE-2019-1003033
Type: osv

## Details
A sandbox bypass vulnerability exists in Jenkins Groovy Plugin 2.1 and earlier in pom.xml, src/main/java/hudson/plugins/groovy/StringScriptSource.java that allows attackers with Overall/Read permission to execute arbitrary code on the Jenkins master JVM.

## References
- http://www.securityfocus.com/bid/107476
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-1338
