# [M] Jenkins ElectricFlow Plugin is vulnerable to stored cross site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fx9p-2qvx-pgjv
CVE: CVE-2019-10335
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fx9p-2qvx-pgjv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:electricflow` — affected >=0 <1.1.7

## Details
The plugin adds metadata displayed on build pages during its operations.

Any user content was not escaped, resulting in a cross-site scripting vulnerability allowing users with Job/Configure permission, or attackers controlling API responses received from ElectricFlow to render arbitrary HTML and JavaScript on Jenkins build pages.

Build metadata is now filtered through a HTML formatter that only allows showing basic HTML, neutralizing any unsafe data. Additionally, all builds executed after the security update is applied will now properly escape content received from ElectricFlow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10335
- https://github.com/jenkinsci/electricflow-plugin/commit/1a90ee7727f8c6925df3e410837ddf6be28cce53
- https://jenkins.io/security/advisory/2019-06-11/#SECURITY-1412
- https://web.archive.org/web/20200227033720/http://www.securityfocus.com/bid/108747
- http://www.openwall.com/lists/oss-security/2019/06/11/1
