# [M] Jenkins PegDown Formatter Plugin has Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-922h-x9qv-2274
CVE: CVE-2019-10374
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-922h-x9qv-2274
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pegdown-formatter` — affected >=0

## Details
PegDown Formatter Plugin uses the PegDown library to implement support for rendering Markdown formatted descriptions in Jenkins. It advertises disabling of HTML to prevent cross-site scripting (XSS) as a feature.

PegDown Formatter Plugin does not prevent the use of `javascript:` scheme in URLs for links. This results in an XSS vulnerability exploitable by users able to configure entities with descriptions or similar properties that are rendered by the configured markup formatter.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10374
- https://github.com/jenkinsci/pegdown-formatter-plugin
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-142
- http://www.openwall.com/lists/oss-security/2019/08/07/1
