# [H] CSRF vulnerability in Config File Provider Plugin 

## Summary
Severity: High
Advisory: GHSA-r5m8-5mwx-cmj8
CVE: CVE-2018-1000414
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r5m8-5mwx-cmj8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:config-file-provider` — affected >=0 <3.2

## Details
A cross-site request forgery vulnerability exists in Jenkins Config File Provider Plugin 3.1 and earlier in ConfigFilesManagement.java, FolderConfigFileAction.java that allows creating and editing configuration file definitions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000414
- https://github.com/jenkinsci/config-file-provider-plugin/commit/5c1df554e44b712e5d926b8d5557c592bf9f0a33
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-938
- http://www.securityfocus.com/bid/106532
