# [M] Jenkins HTML Publisher Plugin vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-q829-hrmc-84c8
CVE: CVE-2019-10432
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q829-hrmc-84c8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:htmlpublisher` — affected >=0 <1.21

## Details
Jenkins HTML Publisher Plugin prior to version 1.21 did not escape the project and build display names in the HTML report frame, resulting in a cross-site scripting vulnerability exploitable by users able to change those. This issue has been patched in version 1.21

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10432
- https://github.com/jenkinsci/htmlpublisher-plugin/commit/637aad0308f8cdfb24610041fcfe815d5a1a096b
- https://access.redhat.com/errata/RHSA-2019:4055
- https://access.redhat.com/errata/RHSA-2019:4089
- https://access.redhat.com/errata/RHSA-2019:4097
- https://github.com/jenkinsci/htmlpublisher-plugin
- https://github.com/jenkinsci/htmlpublisher-plugin/releases/tag/htmlpublisher-1.21
- https://jenkins.io/security/advisory/2019-10-01/#SECURITY-1590
- http://www.openwall.com/lists/oss-security/2019/10/01/2
