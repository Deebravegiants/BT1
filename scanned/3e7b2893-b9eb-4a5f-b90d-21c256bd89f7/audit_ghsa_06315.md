# [M] Statamic: Unsafe method invocation via Antlers template resolution allows data destruction

## Summary
Severity: Medium
Advisory: GHSA-j2vp-f2pv-5rj4
CVE: CVE-2026-64663
CWE: CWE-470
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-j2vp-f2pv-5rj4
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.74.1
- Packagist: `statamic/cms` — affected >=6.0.0 <6.24.0

## Details
### Impact

Manipulating user-supplied input incorporated into Antlers templates could result in the loss of content and assets.

Exploitation requires a site to have templates that pass untrusted input into affected areas. It does not require authentication.

### Patches

This has been fixed in 5.74.1 and 6.24.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-j2vp-f2pv-5rj4
- https://github.com/statamic/cms
