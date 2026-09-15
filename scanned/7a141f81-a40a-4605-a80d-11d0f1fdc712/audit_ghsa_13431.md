# [H] Missing authorization in Jenkins Plug-in for ServiceNow 

## Summary
Severity: High
Advisory: GHSA-cj2x-r74q-vcx9
CVE: CVE-2023-3442
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-cj2x-r74q-vcx9
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:servicenow-devops` — affected >=0 <1.38.1

## Details
A missing authorization vulnerability exists in versions of the Jenkins Plug-in for ServiceNow DevOps prior to 1.38.1 that, if exploited successfully, could cause the unwanted exposure of sensitive information. To address this issue, apply the 1.38.1 version of the Jenkins plug-in for ServiceNow DevOps on your Jenkins server.  No changes are required on your instances of the Now Platform.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3442
- https://github.com/jenkinsci/servicenow-devops-plugin/commit/67192e24099787ad732b41d581f20714d4253921
- https://github.com/jenkinsci/servicenow-devops-plugin/commit/d7d2422b016995402dd245d9c9c5c2f4cf00c691
- https://github.com/jenkinsci/servicenow-devops-plugin
- https://github.com/jenkinsci/servicenow-devops-plugin/releases/tag/v1.38.1
- https://support.servicenow.com/kb?id=kb_article_view&sysparm_article=KB1434119
