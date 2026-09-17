# [H] georgringer/news has SQL Injection in extension "News system" (news)

## Summary
Severity: High
Advisory: GHSA-g868-j3qm-4j28
CVE: CVE-2026-8726
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-g868-j3qm-4j28
Type: github-advisory

## Affected
- Packagist: `georgringer/news` — affected >=12.0.0 <12.3.2
- Packagist: `georgringer/news` — affected >=13.0.0 <13.0.2
- Packagist: `georgringer/news` — affected >=14.0.0 <14.0.3
- Packagist: `georgringer/news` — affected >=0 <10.0.4
- Packagist: `georgringer/news` — affected >=11.0.0 <11.4.4

## Details
The extension fails to properly sanitize user input before using it in a database query. As a result, an unauthenticated attacker can inject arbitrary SQL through a URL parameter on pages using the "Date Menu of news articles" plugin. Exploitation requires the "Date Menu of news articles" plugin to be in use and the TypoScript/Plugin setting disableOverrideDemand not to be enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8726
- https://github.com/FriendsOfPHP/security-advisories/blob/master/georgringer/news/CVE-2026-8726.yaml
- https://github.com/georgringer/news
- https://typo3.org/security/advisory/typo3-ext-sa-2026-010
