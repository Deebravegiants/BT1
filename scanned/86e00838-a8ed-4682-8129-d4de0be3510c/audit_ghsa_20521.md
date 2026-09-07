# [M] XSS vulnerability in translations

## Summary
Severity: Medium
Advisory: GHSA-rrgw-3hg3-9x8c
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-rrgw-3hg3-9x8c
Type: github-advisory

## Affected
- Packagist: `oro/platform` — affected >=3.1.0 <3.1.29
- Packagist: `oro/platform` — affected >=4.1.0 <4.1.17
- Packagist: `oro/platform` — affected >=4.2.0 <4.2.8

## Details
### Summary

An attacker with admin privileges and access to Translations management functionality may add JS payload to translation values via: 
 - Translation management UI.
 - Translations downloaded via the Crowdin service may also contain JS strings used for XSS attacks, for a successful attack poisoned translation should be enabled, downloaded, and installed.
 - Translations uploaded via Upload translation file on the All Languages grid

### Workarounds

There are no workarounds that address this vulnerability.

## References
- https://github.com/oroinc/platform-er/security/advisories/GHSA-rrgw-3hg3-9x8c
