# [M] Stored XSS vulnerability in Jenkins Liquibase Runner Plugin

## Summary
Severity: Medium
Advisory: GHSA-9hg7-xmf8-jxf9
CVE: CVE-2020-2283
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9hg7-xmf8-jxf9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:liquibase-runner` — affected >=0 <1.4.6

## Details
Liquibase Runner Plugin 1.4.5 and earlier does not escape changeset contents when showing them on the build page.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to provide Liquibase changesets evaluated by the plugin.

Liquibase Runner Plugin 1.4.7 no longer supports evaluating changesets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2283
- https://github.com/jenkinsci/liquibase-runner-plugin/commit/4873c19dc921653d994edd6caa9e161c6353c6ae
- https://github.com/jenkinsci/liquibase-runner-plugin
- https://www.jenkins.io/security/advisory/2020-09-23/#SECURITY-1885
- http://www.openwall.com/lists/oss-security/2020/09/23/1
