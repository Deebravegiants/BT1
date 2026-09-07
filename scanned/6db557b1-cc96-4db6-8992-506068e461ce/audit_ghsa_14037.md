# [M] Jenkins TestNG Results Plugin Stored Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h3hg-r97v-5r9w
CVE: CVE-2023-32984
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-h3hg-r97v-5r9w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:testng-plugin` — affected >=0 <730.732.v959a

## Details
Jenkins TestNG Results Plugin 730.v4c5283037693 and earlier does not escape several values that are parsed from TestNG report files and displayed on the plugin’s test information pages.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to provide a crafted TestNG report file.

TestNG Results Plugin 730.732.v959a_3a_a_eb_a_72 escapes the affected values that are parsed from TestNG report files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32984
- https://github.com/jenkinsci/testng-plugin-plugin/commit/5f3d83ca56c0657fc09af7ea70cfbdd691adeaab
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3047
