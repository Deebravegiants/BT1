# [H] Selenium Server (Grid) CSRF

## Summary
Severity: High
Advisory: GHSA-h2rr-m97p-6jq9
CVE: CVE-2022-28108
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-20
Source: https://github.com/advisories/GHSA-h2rr-m97p-6jq9
Type: github-advisory

## Affected
- Maven: `org.seleniumhq.selenium:selenium-grid` — affected >=0 <4.0.0-alpha-7
- Maven: `org.seleniumhq.selenium:selenium-server` — affected >=0

## Details
Selenium Server (Grid) before 4.0.0-alpha-7 allows CSRF because it permits non-JSON content types such as application/x-www-form-urlencoded, multipart/form-data, and text/plain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28108
- https://github.com/SeleniumHQ/selenium
- https://www.gabriel.urdhr.fr/2022/02/07/selenium-standalone-server-csrf-dns-rebinding-rce
- https://www.openwall.com/lists/oss-security/2022/02/07/3
- https://www.openwall.com/lists/oss-security/2022/04/14/2
- https://www.selenium.dev/downloads
