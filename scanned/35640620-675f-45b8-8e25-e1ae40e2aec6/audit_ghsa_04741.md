# [M] Snipe-IT's TOTP is Brute-Forceable Due to Missing Rate Limiting on `POST /two-factor`

## Summary
Severity: Medium
Advisory: GHSA-mr8g-2mj4-pcq2
CVE: CVE-2026-49870
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-mr8g-2mj4-pcq2
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.0

## Details
### Impact
`POST /two-factor` had no rate limiting, lockout, or attempt counter. An attacker with valid credentials can submit unlimited TOTP guesses. The TOTP implementation accepts the current code plus one step on either side (`config/google2fa.php window=1`), so at any instant 3 of 1,000,000 codes are accepted.

After a correct guess the attacker holds a fully authenticated session. If the instance is configured with 2FA in optional mode (`two_factor_enabled='1'`), the attacker can additionally disable 2FA via `POST /account/profile` with `two_factor_optin=0`. No OTP re-verification is required. The account is then accessible with the password alone on future logins. If 2FA is in required-for-all mode (`='2'`), the per-user opt-out path is closed and the impact stops at session-level account takeover. For an admin target, `POST /api/v1/users/two_factor_reset` additionally clears another user's 2FA secret.

### Patches
Patched in v8.6.0

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-mr8g-2mj4-pcq2
- https://github.com/grokability/snipe-it
