# [M] Sulu checks fix permissions for subentities endpoints

## Summary
Severity: Medium
Advisory: GHSA-6h7h-m7p5-hjqp
CVE: CVE-2026-34372
CWE: CWE-288
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-6h7h-m7p5-hjqp
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=1.0.0 <2.6.22
- Packagist: `sulu/sulu` — affected >=3.0.0 <3.0.5

## Details
### Impact

A user which has permission for the Sulu Admin via atleast one role could have access to the subentities of contacts via the admin API without even have permission for contacts.

### Patches

The issue was patched in release 2.6.22 and 3.0.5.

### Workarounds

Create a Symfony Request Listener checking the permissions for the specific roles.

### Resources

Github Advisory: https://github.com/sulu/sulu/security/advisories/GHSA-6h7h-m7p5-hjqp

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-6h7h-m7p5-hjqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34372
- https://github.com/sulu/sulu
- https://github.com/sulu/sulu/releases/tag/2.6.22
- https://github.com/sulu/sulu/releases/tag/3.0.5
