# [M] Credentials stored in plain text by Jenkins Bumblebee HP ALM Plugin

## Summary
Severity: Medium
Advisory: GHSA-8v72-qr3h-c6rv
CVE: CVE-2021-21614
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8v72-qr3h-c6rv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:bumblebee` — affected >=0 <4.1.6

## Details
Jenkins Bumblebee HP ALM Plugin 4.1.5 and earlier stores credentials unencrypted in its global configuration file `com.agiletestware.bumblebee.BumblebeeGlobalConfig.xml` on the Jenkins controller as part of its configuration.

These credentials can be viewed by users with access to the Jenkins controller file system.

Jenkins Bumblebee HP ALM Plugin 4.1.6 stores credentials encrypted once its configuration is saved again.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21614
- https://github.com/jenkinsci/bumblebee-plugin/commit/7faf4bd6e702726bb7542f370cbdedcbfa340443
- https://github.com/jenkinsci/bumblebee-plugin
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2156
