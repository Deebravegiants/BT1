# [C] Rambox RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-2gc6-2h2g-ph48
CVE: CVE-2019-17625
CWE: CWE-78, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2gc6-2h2g-ph48
Type: github-advisory

## Affected
- npm: `Rambox` — affected >=0

## Details
There is a stored XSS in Rambox 0.6.9 that can lead to code execution. The XSS is in the name field while adding/editing a service. The problem occurs due to incorrect sanitization of the name field when being processed and stored. This allows a user to craft a payload for Node.js and Electron, such as an exec of OS commands within the onerror attribute of an IMG element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17625
- https://github.com/Ekultek/CVE-2019-17625
- https://github.com/ramboxapp/community-edition
- https://web.archive.org/web/20211209122051/https://github.com/ramboxapp/community-edition/issues/2418
