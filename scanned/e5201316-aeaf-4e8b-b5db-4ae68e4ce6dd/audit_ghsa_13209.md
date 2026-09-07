# [M] Stored XSS vulnerability in Jenkins TAP Plugin

## Summary
Severity: Medium
Advisory: GHSA-3vcr-579j-4x48
CVE: CVE-2023-41940
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-3vcr-579j-4x48
Type: github-advisory

## Affected
- Maven: `org.tap4j:tap` — affected >=0

## Details
Jenkins TAP Plugin 2.3 and earlier does not escape TAP file contents, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control TAP file contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41940
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3190
- http://www.openwall.com/lists/oss-security/2023/09/06/9
