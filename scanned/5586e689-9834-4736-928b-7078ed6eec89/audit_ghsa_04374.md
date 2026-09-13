# [M] Craft Commerce: Coupon Code Brute-Force via Rate Limit Bypass

## Summary
Severity: Medium
Advisory: GHSA-h5gm-x9wr-vhcm
CVE: CVE-2026-55795
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-h5gm-x9wr-vhcm
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.6.5
- Packagist: `craftcms/commerce` — affected >=4.0.0 <4.11.2

## Details
### Summary

The CartController defines a RateLimiter behavior that is only activated when the 'number' POST/GET parameter is explicitly provided.

### Details

When an attacker submits coupon codes against the session-based cart (without passing a 'number' parameter), no rate limiting is applied. This allows unlimited attempts to guess coupon codes.

**Vulnerable Code**
<img width="864" height="90" alt="resim" src="https://github.com/user-attachments/assets/a5197f10-f1fd-4331-93f9-9479d0ceebba" />

<img width="881" height="272" alt="resim" src="https://github.com/user-attachments/assets/d9db963f-5d1f-4b00-a4b4-5f2dfe2b71dd" />

<img width="861" height="271" alt="resim" src="https://github.com/user-attachments/assets/f7842493-3bc0-4e99-956c-7266bab15703" />

### PoC
Complete instructions, including specific configuration details, to reproduce the vulnerability.

<img width="909" height="171" alt="resim" src="https://github.com/user-attachments/assets/cfc8c994-5e0c-48de-b728-464029beba0e" />

### Impact
An attacker can enumerate all coupon codes through automated requests.

**Remediation**
Apply rate limiting unconditionally on actionUpdateCart regardless of whether 'number' is present.

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-h5gm-x9wr-vhcm
- https://github.com/craftcms/commerce/commit/df22c4f9c4ea7fb7857d833f755e49ea6f9f5bb5
- https://github.com/craftcms/commerce
