# [H] LTI 1.3 Tool Library's Nonce Claim Value not validated against nonce value sent in Authentication Request before v5.0

## Summary
Severity: High
Advisory: GHSA-5p73-qg2v-383h
CVE: CVE-2022-31158
CWE: CWE-294, CWE-327
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-5p73-qg2v-383h
Type: github-advisory

## Affected
- Packagist: `packbackbooks/lti-1-3-php-library` — affected >=0 <5.0

## Details
### Impact

Nonce Claim Value was not being validated against the nonce value sent in the Authentication Request.

### Patches

Users should upgrade to version 5.0 immediately

### Workarounds

None.

## References
- https://github.com/packbackbooks/lti-1-3-php-library/security/advisories/GHSA-5p73-qg2v-383h
- https://nvd.nist.gov/vuln/detail/CVE-2022-31158
- https://github.com/packbackbooks/lti-1-3-php-library
- https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
