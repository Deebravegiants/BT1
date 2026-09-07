# [M] Jenkins Publisher Over CIFS Plugin confused deputy vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rf7h-9m85-535v
CVE: CVE-2018-1999038
CWE: CWE-441
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rf7h-9m85-535v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:publish-over-cifs` — affected >=0 <0.11

## Details
A confused deputy vulnerability exists in Jenkins Publisher Over CIFS Plugin 0.10 and earlier in CifsPublisherPluginDescriptor.java that allows attackers to have Jenkins connect to an attacker specified CIFS server with attacker specified credentials. Additionally, this form validation method did not require POST requests, resulting in a CSRF vulnerability. As of version 0.11, this form validation method requires POST requests and Overall/Administer permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999038
- https://github.com/jenkinsci/publish-over-cifs-plugin/commit/9402d8c1044508c2fc30a5dd1e34afe6819616a0
- https://github.com/jenkinsci/publish-over-cifs-plugin
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-975
