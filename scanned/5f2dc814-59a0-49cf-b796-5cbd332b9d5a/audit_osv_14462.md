# [H] CVE-2019-1003006

## Summary
Severity: High
Advisory: CVE-2019-1003006
Aliases: GHSA-xfwj-2f34-32f5
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-06
Source: https://osv.dev/vulnerability/CVE-2019-1003006
Type: osv

## Details
A sandbox bypass vulnerability exists in Jenkins Groovy Plugin 2.0 and earlier in src/main/java/hudson/plugins/groovy/StringScriptSource.java that allows attackers with Overall/Read permission to provide a Groovy script to an HTTP endpoint that can result in arbitrary code execution on the Jenkins master JVM.

## References
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1293
