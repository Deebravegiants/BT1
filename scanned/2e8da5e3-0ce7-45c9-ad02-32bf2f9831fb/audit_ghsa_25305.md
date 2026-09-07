# [M] Redgate SQL Change Automation Plugin stored credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-x23m-8c2h-6wg7
CVE: CVE-2020-2095
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x23m-8c2h-6wg7
Type: github-advisory

## Affected
- Maven: `com.redgate.plugins.redgatesqlci:redgate-sql-ci` — affected >=0 <2.0.5

## Details
Redgate SQL Change Automation Plugin 2.0.4 and earlier stores a NuGet API key unencrypted in job config.xml files as part of its configuration. This credential could be viewed by users with Extended Read permission or access to the Jenkins controller file system.

This is due to an incomplete fix of [SECURITY-1598](https://www.jenkins.io/security/advisory/2019-12-17/#SECURITY-1598).

Redgate SQL Change Automation Plugin 2.0.5 now stores the API key encrypted. Existing jobs need to have their configuration saved for existing plain text passwords to be overwritten.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2095
- https://github.com/jenkinsci/redgate-sql-ci-plugin/commit/962f1770eeb1f18dfac91d12461fa6db566e769e
- https://github.com/jenkinsci/redgate-sql-ci-plugin
- https://jenkins.io/security/advisory/2020-01-15/#SECURITY-1696
