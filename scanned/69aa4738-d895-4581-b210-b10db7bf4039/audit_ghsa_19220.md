# [C] BoniGarcia WebDriverManager Affected By Improper Restriction of XML External Entity Reference

## Summary
Severity: Critical
Advisory: GHSA-pwm3-776c-8q7q
CVE: CVE-2025-4641
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:H/SC:H/SI:L/SA:H (CVSS_V4)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-pwm3-776c-8q7q
Type: github-advisory

## Affected
- Maven: `io.github.bonigarcia:webdrivermanager` — affected >=1.0.0 <6.1.0

## Details
Improper Restriction of XML External Entity Reference vulnerability in bonigarcia webdrivermanager on Windows, MacOS, Linux (XML parsing components modules) allows Data Serialization External Entities Blowup. This vulnerability is associated with program files src/main/java/io/github/bonigarcia/wdm/WebDriverManager.java.

This issue affects webdrivermanager: from 1.0.0 before 6.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4641
- https://github.com/bonigarcia/webdrivermanager/pull/1458
- https://github.com/bonigarcia/webdrivermanager
