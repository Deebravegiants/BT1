# [M] Stored XSS vulnerability in Code Coverage API Plugin

## Summary
Severity: Medium
Advisory: GHSA-xg77-xqhq-crpr
CVE: CVE-2020-2106
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xg77-xqhq-crpr
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:code-coverage-api` — affected >=0 <1.1.3

## Details
Code Coverage API Plugin 1.1.2 and earlier does not escape the filename of the coverage report used in its view.

This results in a stored cross-site scripting vulnerability that can be exploited by users able to change the job configuration.

Code Coverage API Plugin 1.1.3 escapes the filename of the coverage report used in its view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2106
- https://github.com/jenkinsci/code-coverage-api-plugin/commit/24921da6d625c4deb259049446dc2b45b1da4603
- https://github.com/jenkinsci/code-coverage-api-plugin
- https://jenkins.io/security/advisory/2020-01-29/#SECURITY-1680
- http://www.openwall.com/lists/oss-security/2020/01/29/1
