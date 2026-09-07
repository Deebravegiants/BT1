# [M] Ibexa RichText Field Type XSS vulnerabilities in back office

## Summary
Severity: Medium
Advisory: GHSA-9qv6-4pwm-m68f
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-9qv6-4pwm-m68f
Type: github-advisory

## Affected
- Packagist: `ibexa/fieldtype-richtext` — affected >=4.6.0-beta1 <4.6.21

## Details
### Impact
This security advisory is a part of IBEXA-SA-2025-003, which resolves XSS vulnerabilities in several parts of the back office of Ibexa DXP. Back office access and varying levels of editing and management permissions are required to exploit these vulnerabilities. This typically means Editor or Administrator role, or similar. Injected XSS is persistent and can be reflected in the front office, possibly affecting end users. The fixes ensure XSS is escaped, and any existing injected XSS is rendered harmless.

### Patches
- See "Patched versions".
- https://github.com/ibexa/fieldtype-richtext/commit/4a4a170c7faa4807ae0f74c581481b835bab3caf

### Workarounds
None.

## References
- https://github.com/ibexa/fieldtype-richtext/security/advisories/GHSA-9qv6-4pwm-m68f
- https://github.com/ibexa/fieldtype-richtext/commit/4a4a170c7faa4807ae0f74c581481b835bab3caf
- https://developers.ibexa.co/security-advisories/ibexa-sa-2025-003-xss-vulnerabilities-in-back-office
- https://github.com/ibexa/fieldtype-richtext
