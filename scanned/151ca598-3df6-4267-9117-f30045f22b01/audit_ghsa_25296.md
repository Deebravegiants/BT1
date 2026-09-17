# [M] Jenkins ElectricFlow Plugin Missing permission checks

## Summary
Severity: Medium
Advisory: GHSA-m8f2-9282-x38v
CVE: CVE-2019-10333
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m8f2-9282-x38v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:electricflow` — affected >=0 <1.1.7

## Details
Various form validation and form autocompletion methods in CloudBees CD Plugin lacked permission checks. This allowed attackers with Overall/Read access to obtain information about the configuration of CloudBees CD Plugin, as well as the configuration and data of connected ElectricFlow servers.

These form validation and autocompletion methods now require Overall/Administer or Job/Configure permission, as appropriate for the given method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10333
- https://jenkins.io/security/advisory/2019-06-11/#SECURITY-1410%20(2)
- https://web.archive.org/web/20200227033720/http://www.securityfocus.com/bid/108747
- http://www.openwall.com/lists/oss-security/2019/06/11/1
