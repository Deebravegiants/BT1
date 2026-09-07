# [H] Cross Site Request Forgery in Jenkins Storable Configs Plugin

## Summary
Severity: High
Advisory: GHSA-rr2r-g6xm-58xj
CVE: CVE-2022-30972
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-rr2r-g6xm-58xj
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:storable-configs-plugin` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Storable Configs Plugin 1.0 and earlier allows attackers to have Jenkins parse a local XML file (e.g., archived artifacts) that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30972
- https://github.com/jenkinsci/storable-configs-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-1969
