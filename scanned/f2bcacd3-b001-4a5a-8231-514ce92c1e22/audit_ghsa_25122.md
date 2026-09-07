# [M] Stored XSS vulnerability in Config File Provider Plugin 

## Summary
Severity: Medium
Advisory: GHSA-vwfm-42q6-qj75
CVE: CVE-2018-1000413
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vwfm-42q6-qj75
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:config-file-provider` — affected >=0 <3.2

## Details
A cross-site scripting vulnerability exists in Jenkins Config File Provider Plugin 3.1 and earlier in configfiles.jelly, providerlist.jelly that allows users with the ability to configure configuration files to insert arbitrary HTML into some pages in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000413
- https://github.com/jenkinsci/config-file-provider-plugin/commit/5c1df554e44b712e5d926b8d5557c592bf9f0a33
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-1080
- http://www.securityfocus.com/bid/106532
