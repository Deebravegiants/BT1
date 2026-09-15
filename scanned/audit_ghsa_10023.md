# [H] LiteLLM: Password hash exposure and pass-the-hash authentication bypass

## Summary
Severity: High
Advisory: GHSA-69x8-hrgq-fjj8
CWE: CWE-200, CWE-327, CWE-916
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-69x8-hrgq-fjj8
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.83.0

## Details
### Impact

Three issues combine into a full authentication bypass chain:

1. Weak hashing: User passwords are stored as unsalted SHA-256 hashes, making them vulnerable to rainbow table attacks and trivially identifying users with identical passwords.
2. Hash exposure: Multiple API endpoints (/user/info, /user/update, /spend/users) return the password hash field in responses to any authenticated user regardless of role. Plaintext passwords could also potentially be exposed in certain scenarios.
4. Pass-the-hash: The /v2/login endpoint accepts the raw SHA-256 hash as a valid password without re-hashing, allowing direct login with a stolen

An already authenticated user can retrieve another user's password hash from the API and use it to log in as that user. This enables full privilege escalation in three HTTP requests.

### Patches

Fixed in v1.83.0. Passwords are now hashed with scrypt (random 16-byte salt, n=16384, r=8, p=1). Password hashes are stripped from all API responses. Existing SHA-256 hashes are transparently migrated on next login.

## References
- https://github.com/BerriAI/litellm/security/advisories/GHSA-69x8-hrgq-fjj8
- https://github.com/BerriAI/litellm
