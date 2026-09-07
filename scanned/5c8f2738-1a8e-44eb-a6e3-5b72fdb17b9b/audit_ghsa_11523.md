# [M] Statamic has an Open Redirect on unauthenticated endpoints via URL parsing differential

## Summary
Severity: Medium
Advisory: GHSA-7f74-7q5w-hj4r
CVE: CVE-2026-33885
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-7f74-7q5w-hj4r
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.16
- Packagist: `statamic/cms` — affected >=6.0.0.alpha.1 <6.7.2

## Details
### Impact
The external URL detection used for redirect validation on unauthenticated endpoints could be bypassed, allowing users to be redirected to external URLs after actions like form submissions and authentication flows.

### Patches
This has been fixed in 5.73.16 and 6.7.2.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-7f74-7q5w-hj4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33885
- https://github.com/statamic/cms
