# [M] Fluid Components TYPO3 extension vulnerable to Cross-Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-8648-h559-8h42
CVE: CVE-2023-28604
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-8648-h559-8h42
Type: github-advisory

## Affected
- Packagist: `sitegeist/fluid-components` — affected >=0 <3.5.0

## Details
All versions of Fluid Components before 3.5.0 were susceptible to Cross-Site Scripting. Version 3.5.0 of the extension fixes this issue. Due to the nature of the problem, some changes in your project's Fluid templates might be necessary to prevent unwanted double-escaping of HTML markup.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28604
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sitegeist/fluid-components/CVE-2023-28604.yaml
- https://github.com/sitegeist/fluid-components
- https://github.com/sitegeist/fluid-components/blob/master/Documentation/XssIssue.md
- https://typo3.org/security/advisory/typo3-ext-sa-2023-003
