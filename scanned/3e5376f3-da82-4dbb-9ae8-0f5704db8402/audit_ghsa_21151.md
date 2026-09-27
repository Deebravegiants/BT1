# [H] LTI 1.3 Tool Library's function used to generate random nonces not sufficiently cryptographically complex before v5.0

## Summary
Severity: High
Advisory: GHSA-768m-5w34-2xf5
CVE: CVE-2022-31157
CWE: CWE-327, CWE-330
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-768m-5w34-2xf5
Type: github-advisory

## Affected
- Packagist: `packbackbooks/lti-1-3-php-library` — affected >=0 <5.0

## Details
### Impact

The function used to generate random nonces was not sufficiently cryptographically complex. As a result values may be predictable and tokens may be forgable.

### Patches

Users should upgrade to version 5.0 immediately

### Workarounds

None.

## References
- https://github.com/packbackbooks/lti-1-3-php-library/security/advisories/GHSA-768m-5w34-2xf5
- https://nvd.nist.gov/vuln/detail/CVE-2022-31157
- https://github.com/packbackbooks/lti-1-3-php-library/commit/de19e8a0b28cdc7750fa3ca98471eeed26ba3e57
- https://github.com/packbackbooks/lti-1-3-php-library
- https://openid.net/specs/openid-connect-core-1_0.html#IDToken
