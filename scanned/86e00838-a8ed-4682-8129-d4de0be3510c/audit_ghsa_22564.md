# [M] Jenkins Config File Provider Plugin XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pmc5-74w3-78mw
CVE: CVE-2019-1003014
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pmc5-74w3-78mw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:config-file-provider` — affected >=0 <3.5

## Details
An cross-site scripting vulnerability exists in Jenkins Config File Provider Plugin 3.4.1 and earlier in src/main/resources/lib/configfiles/configfiles.jelly that allows attackers with permission to define shared configuration files to execute arbitrary JavaScript when a user attempts to delete the shared configuration file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003014
- https://github.com/jenkinsci/config-file-provider-plugin/commit/64fba993c897ff52a9c6c38c6c41806f2e8cc73f
- https://access.redhat.com/errata/RHBA-2019:0326
- https://access.redhat.com/errata/RHBA-2019:0327
- https://github.com/jenkinsci/config-file-provider-plugin
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1253
