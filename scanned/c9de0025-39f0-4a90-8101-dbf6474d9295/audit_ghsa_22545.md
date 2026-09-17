# [M] Information disclosure in Azure VM Agents Plugin 

## Summary
Severity: Medium
Advisory: GHSA-3hg6-c7f8-3348
CVE: CVE-2019-1003035
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3hg6-c7f8-3348
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-vm-agents` — affected >=0 <0.8.1

## Details
An information exposure vulnerability exists in Jenkins Azure VM Agents Plugin 0.8.0 and earlier in src/main/java/com/microsoft/azure/vmagent/AzureVMAgentTemplate.java, src/main/java/com/microsoft/azure/vmagent/AzureVMCloud.java that allows attackers with Overall/Read permission to perform the 'verify configuration' form validation action, thereby obtaining limited information about the Azure configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003035
- https://github.com/jenkinsci/azure-vm-agents-plugin/commit/91bfc7d95ae1349ce2a8b6b7e73155848fdc1d82
- https://github.com/jenkinsci/azure-vm-agents-plugin
- https://jenkins.io/security/advisory/2019-03-06/#SECURITY-1330
- http://www.securityfocus.com/bid/107476
