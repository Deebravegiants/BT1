# [M] Jenkins Google Login Plugin 1.0 and 1.1 allows anonymous users to authenticate through client-side request modification

## Summary
Severity: Medium
Advisory: GHSA-p487-39h9-hm84
CVE: CVE-2015-5298
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-07-08
Source: https://github.com/advisories/GHSA-p487-39h9-hm84
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-login` — affected >=1.0 <1.2

## Details
The Google Login Plugin (versions 1.0 and 1.1) allows malicious anonymous users to authenticate successfully against Jenkins instances that are supposed to be locked down to a particular Google Apps domain through client-side request modification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5298
- https://github.com/jenkinsci/google-login-plugin
- https://www.jenkins.io/security/advisory/2015-10-12
- http://exfiltrated.com/research-CVE-2015-5298.php
