# [M] Credentials stored in plain text by Jenkins TraceTronic ECU-TEST Plugin

## Summary
Severity: Medium
Advisory: GHSA-qvjr-x8fw-hghv
CVE: CVE-2021-21612
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qvjr-x8fw-hghv
Type: github-advisory

## Affected
- Maven: `de.tracetronic.jenkins.plugins:ecutest` — affected >=0 <2.24

## Details
Jenkins TraceTronic ECU-TEST Plugin 2.23.1 and earlier stores credentials unencrypted in its global configuration file `de.tracetronic.jenkins.plugins.ecutest.report.atx.installation.ATXInstallation.xml` on the Jenkins controller as part of its configuration.

These credentials can be viewed by users with access to the Jenkins controller file system.

Jenkins TraceTronic ECU-TEST Plugin 2.24 adds a new option type for sensitive options. Previously stored credentials are migrated to that option type on Jenkins startup.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21612
- https://github.com/jenkinsci/ecutest-plugin
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2057
