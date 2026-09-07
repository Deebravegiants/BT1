# [H] XML External Entity Reference in Jenkins Storable Configs Plugin

## Summary
Severity: High
Advisory: GHSA-wqmp-2p5r-rhfv
CVE: CVE-2022-30971
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-wqmp-2p5r-rhfv
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:storable-configs-plugin` — affected >=0

## Details
Jenkins Storable Configs Plugin 1.0 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers with Item/Configure permission to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30971
- https://github.com/jenkinsci/storable-configs-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-1969
