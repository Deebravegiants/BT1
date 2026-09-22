# [M] SSRF vulnerability due to missing permission check in Jenkins OctopusDeploy Plugin 

## Summary
Severity: Medium
Advisory: GHSA-5v2j-w677-j4mp
CVE: CVE-2019-1003027
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5v2j-w677-j4mp
Type: github-advisory

## Affected
- Maven: `hudson.plugins.octopusdeploy:octopusdeploy` — affected >=0 <1.9.0

## Details
A server-side request forgery vulnerability exists in Jenkins OctopusDeploy Plugin 1.8.1 and earlier in OctopusDeployPlugin.java that allows attackers with Overall/Read permission to have Jenkins connect to an attacker-specified URL and obtain the HTTP response code if successful, and exception error message otherwise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003027
- https://jenkins.io/security/advisory/2019-02-19/#SECURITY-817
- http://www.securityfocus.com/bid/107295
