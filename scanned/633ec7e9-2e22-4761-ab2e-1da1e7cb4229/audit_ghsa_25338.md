# [M] Missing permission check in Azure VM Agents Plugin allowed modifying VM configuration 

## Summary
Severity: Medium
Advisory: GHSA-m33c-cjjj-2mg4
CVE: CVE-2019-1003036
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m33c-cjjj-2mg4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-vm-agents` — affected >=0 <0.8.1

## Details
A data modification vulnerability exists in Jenkins Azure VM Agents Plugin 0.8.0 and earlier in src/main/java/com/microsoft/azure/vmagent/AzureVMAgent.java that allows attackers with Overall/Read permission to attach a public IP address to an Azure VM agent.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003036
- https://github.com/jenkinsci/azure-vm-agents-plugin/commit/6cf1e11778993988ded08eb15ea051541341ec12
- https://github.com/jenkinsci/azure-vm-agents-plugin
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-1331
- http://www.securityfocus.com/bid/107476
