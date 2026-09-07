# [C] Improper Control of Generation of Code in Jenkins Script Security Plugin

## Summary
Severity: Critical
Advisory: GHSA-72gx-qq2m-6xr2
CVE: CVE-2019-10431
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-72gx-qq2m-6xr2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.65

## Details
A sandbox bypass vulnerability in Jenkins Script Security Plugin 1.64 and earlier related to the handling of default parameter expressions in constructors allowed attackers to execute arbitrary code in sandboxed scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10431
- https://github.com/jenkinsci/script-security-plugin/commit/415b6e2f3fa0c2e4bd2f9c4a589a9e1fc9cbac8b
- https://access.redhat.com/errata/RHSA-2019:4055
- https://access.redhat.com/errata/RHSA-2019:4089
- https://access.redhat.com/errata/RHSA-2019:4097
- https://github.com/jenkinsci/script-security-plugin
- https://github.com/jenkinsci/script-security-plugin/blob/7bd58b8635709cecdb50018844e5d6dbe1ce13ea/CHANGELOG.md
- https://jenkins.io/security/advisory/2019-10-01/#SECURITY-1579
- http://www.openwall.com/lists/oss-security/2019/10/01/2
