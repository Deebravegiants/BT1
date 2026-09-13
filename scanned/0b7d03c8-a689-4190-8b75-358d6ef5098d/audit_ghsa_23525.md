# [M] Unprivileged users with Overall/Read access are able to enumerate credential IDs in Azure VM Agents Plugin

## Summary
Severity: Medium
Advisory: GHSA-r2vw-x3hr-969v
CVE: CVE-2019-1003037
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r2vw-x3hr-969v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-vm-agents` — affected >=0 <0.8.1

## Details
An information exposure vulnerability exists in Jenkins Azure VM Agents Plugin 0.8.0 and earlier in src/main/java/com/microsoft/azure/vmagent/AzureVMCloud.java that allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003037
- https://github.com/jenkinsci/azure-vm-agents-plugin/commit/e36c8a9b0a436d3b79dc14b5cb4f7f6032fedd3f
- https://github.com/jenkinsci/azure-vm-agents-plugin
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-1332
- http://www.securityfocus.com/bid/107476
