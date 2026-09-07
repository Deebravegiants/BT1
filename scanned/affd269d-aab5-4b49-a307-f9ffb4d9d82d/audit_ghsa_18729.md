# [M] ibexa/fieldtype-richtext has an XSS vulnerability via acronym custom tag in Rich Text

## Summary
Severity: Medium
Advisory: GHSA-8c2g-f8jm-5cr7
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-10-17
Source: https://github.com/advisories/GHSA-8c2g-f8jm-5cr7
Type: github-advisory

## Affected
- Packagist: `ibexa/fieldtype-richtext` — affected >=5.0.0 <5.0.3
- Packagist: `ibexa/fieldtype-richtext` — affected >=4.6.0 <4.6.25

## Details
### Impact
This security advisory resolves an XSS vulnerability in acronym custom tag in Rich Text, in the back office of the DXP. Back office access and varying levels of editing and management permissions are required to exploit this vulnerability. This typically means Editor or Administrator role, or similar. Injected XSS is persistent and may in some cases be reflected in the front office, possibly affecting end users. The fixes ensure XSS is escaped, and any existing injected XSS is rendered harmless.

### Patches
See "Patched versions".

### Workarounds
None.

### References
https://developers.ibexa.co/security-advisories/ibexa-sa-2025-004-xss-and-enumeration-vulnerabilities-in-back-office

## References
- https://github.com/ibexa/fieldtype-richtext/security/advisories/GHSA-8c2g-f8jm-5cr7
- https://developers.ibexa.co/security-advisories/ibexa-sa-2025-004-xss-and-enumeration-vulnerabilities-in-back-office
- https://github.com/ibexa/fieldtype-richtext
