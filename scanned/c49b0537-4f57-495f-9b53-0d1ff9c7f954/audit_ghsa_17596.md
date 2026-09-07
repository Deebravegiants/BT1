# [M] Ibexa eZ Platform Admin UI assets XSS vulnerabilities in back office

## Summary
Severity: Medium
Advisory: GHSA-r5rx-53g9-25rj
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-r5rx-53g9-25rj
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-admin-ui-assets` — affected >=5.3.0-beta1 <5.3.5

## Details
### Impact
This security advisory is a part of IBEXA-SA-2025-003, which resolves XSS vulnerabilities in several parts of the back office of Ibexa DXP. Back office access and varying levels of editing and management permissions are required to exploit these vulnerabilities. This typically means Editor or Administrator role, or similar. Injected XSS is persistent and can be reflected in the front office, possibly affecting end users. The fixes ensure XSS is escaped, and any existing injected XSS is rendered harmless.

### Patches
- See "Patched versions".
- https://github.com/ezsystems/ezplatform-admin-ui-assets/commit/219b71b70aaea9321947d2dbeb49fff1b49e05f4

### Workarounds
None.

## References
- https://github.com/ezsystems/ezplatform-admin-ui-assets/security/advisories/GHSA-r5rx-53g9-25rj
- https://github.com/ezsystems/ezplatform-admin-ui-assets/commit/219b71b70aaea9321947d2dbeb49fff1b49e05f4
- https://developers.ibexa.co/security-advisories/ibexa-sa-2025-003-xss-vulnerabilities-in-back-office
- https://github.com/ezsystems/ezplatform-admin-ui-assets
