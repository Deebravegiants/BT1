# [C] Server-Side Template Injection in extension "Event management and registration" (sf_event_mgt)

## Summary
Severity: Critical
Advisory: CVE-2026-77129
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-77129
Type: osv

## Details
The extension passes an editor-configurable email subject string directly into a Fluid template source without restriction. A backend user with edit access to the event plugin or Backend Module can supply Fluid ViewHelper syntax in this field to disclose sensitive data or execute TypoScript content objects. Exploitation of this issue requires an authenticated backend account with edit access to the event registration plugin or backend module.

## References
- https://packagist.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77129.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77129
- https://typo3.org/security/advisory/typo3-ext-sa-2026-023
- https://github.com/derhansen/sf_event_mgt
