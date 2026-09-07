# [H] Jenkins Lucene-Search Plugin vulnerable to reflected (XSS) cross-site scripting

## Summary
Severity: High
Advisory: GHSA-6954-h5c8-m29f
CVE: CVE-2022-36922
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-6954-h5c8-m29f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:lucene-search` — affected >=0 <387.v938a

## Details
Jenkins Lucene-Search Plugin 370.v62a5f618cd3a and earlier does not escape the search query parameter displayed on the search result page.

This results in a reflected cross-site scripting (XSS) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36922
- https://github.com/jenkinsci/lucene-search-plugin/commit/5f9fd00d83a5a73a7b9579e8139b3db3a9065ed2
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2812
- http://www.openwall.com/lists/oss-security/2022/07/27/1
