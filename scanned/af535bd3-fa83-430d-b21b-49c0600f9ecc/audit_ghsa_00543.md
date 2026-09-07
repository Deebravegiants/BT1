# [M] OWASP AntiSamy Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q44v-xc3g-v7jq
CVE: CVE-2017-14735
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-q44v-xc3g-v7jq
Type: github-advisory

## Affected
- Maven: `org.owasp.antisamy:antisamy` — affected >=0 <1.5.7

## Details
OWASP AntiSamy before 1.5.7 allows XSS via HTML5 entities, as demonstrated by use of &colon; to construct a javascript: URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14735
- https://github.com/nahsra/antisamy/issues/10
- https://github.com/advisories/GHSA-q44v-xc3g-v7jq
- https://github.com/nahsra/antisamy
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.securityfocus.com/bid/105656
