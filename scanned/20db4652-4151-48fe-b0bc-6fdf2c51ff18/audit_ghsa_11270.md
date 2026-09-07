# [M] Statamic's Markdown preview endpoint exposes sensitive user data

## Summary
Severity: Medium
Advisory: GHSA-cvh3-23vq-w7h4
CVE: CVE-2026-33882
CWE: CWE-20, CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-cvh3-23vq-w7h4
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.16
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.7.2

## Details
### Impact
The markdown preview endpoint could be manipulated to return augmented data from arbitrary fieldtypes. With the users fieldtype specifically, an authenticated control panel user could retrieve sensitive user data including email addresses, encrypted passkey data, and encrypted two-factor authentication codes.

### Patches
This has been fixed in 5.73.16 and 6.7.2.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-cvh3-23vq-w7h4
- https://nvd.nist.gov/vuln/detail/CVE-2026-33882
- https://github.com/statamic/cms
