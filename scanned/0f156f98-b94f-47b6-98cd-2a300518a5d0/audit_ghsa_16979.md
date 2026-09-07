# [M] Passbolt API allows HTML injection

## Summary
Severity: Medium
Advisory: GHSA-2pg6-vw9c-qhjv
CVE: CVE-2024-33670
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-26
Source: https://github.com/advisories/GHSA-2pg6-vw9c-qhjv
Type: github-advisory

## Affected
- Packagist: `passbolt/passbolt_api` — affected >=0 <4.6.2

## Details
Passbolt API before 4.6.2 allows HTML injection in a URL parameter, resulting in custom content being displayed when a user visits the crafted URL. Although the injected content is not executed as JavaScript due to Content Security Policy (CSP) restrictions, it may still impact the appearance and user interaction of the page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33670
- https://github.com/passbolt/passbolt_api/commit/5c537849040990086dcd5013b5bb009e1dad3fb6
- https://help.passbolt.com/incidents/reflective-html-injection-vulnerability
