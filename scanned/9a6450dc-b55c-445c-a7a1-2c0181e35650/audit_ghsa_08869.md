# [M] Sulu: Weak Cryptographical usage for API Key generation and Reset Tokens

## Summary
Severity: Medium
Advisory: GHSA-7fv8-6pp7-6h85
CVE: CVE-2026-45701
CWE: CWE-327
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-7fv8-6pp7-6h85
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=3.0.0-alpha1 <3.0.6
- Packagist: `sulu/sulu` — affected >=0 <2.6.23

## Details
### Impact

The password reset tokenand API key generation uses a weak cryptographical hash algorithm.

### Patches

Fixed in 2.6.23 and 3.0.6 version.

### Workarounds

Patch the related `User.php` and `ResettingController.php` file in the SecurityBundle.

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-7fv8-6pp7-6h85
- https://nvd.nist.gov/vuln/detail/CVE-2026-45701
- https://github.com/sulu/sulu
- https://github.com/sulu/sulu/releases/tag/2.6.23
- https://github.com/sulu/sulu/releases/tag/3.0.6
