# [H] Jenkins Pipeline Declarative Plugin sandbox bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-x6jx-cxg3-mggh
CVE: CVE-2019-1003002
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x6jx-cxg3-mggh
Type: github-advisory

## Affected
- Maven: `org.jenkinsci.plugins:pipeline-model-definition` — affected >=0 <1.3.4.1

## Details
Jenkins Script Security sandbox protection could be circumvented during the script compilation phase by applying AST transforming annotations such as `@Grab` to source code elements.

Both the pipeline validation REST APIs and actual script/pipeline execution are affected.

This allowed users with Overall/Read permission, or able to control Jenkinsfile or sandboxed Pipeline shared library contents in SCM, to bypass the sandbox protection and execute arbitrary code on the Jenkins controller.

All known unsafe AST transformations in Groovy are now prohibited in sandboxed scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003002
- https://github.com/jenkinsci/pipeline-model-definition-plugin/commit/083abd96e68fd89f556a0cd53db5f878dbf09b92
- https://access.redhat.com/errata/RHBA-2019:0326
- https://access.redhat.com/errata/RHBA-2019:0327
- https://jenkins.io/security/advisory/2019-01-08/#SECURITY-1266
- https://www.exploit-db.com/exploits/46572
- http://packetstormsecurity.com/files/152132/Jenkins-ACL-Bypass-Metaprogramming-Remote-Code-Execution.html
- http://www.rapid7.com/db/modules/exploit/multi/http/jenkins_metaprogramming
