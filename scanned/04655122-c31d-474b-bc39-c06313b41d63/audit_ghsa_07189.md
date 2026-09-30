# [H] Kimai: Pre-2FA KIMAI_SESSION cookie grants full authenticated REST API access, bypassing TOTP

## Summary
Severity: High
Advisory: GHSA-v8hx-4vx8-wc96
CVE: CVE-2026-52827
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-v8hx-4vx8-wc96
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.59.0

## Details
### Summary
Two-factor authentication (TOTP) can be fully bypassed for the REST API. The `KIMAI_SESSION` cookie returned in the response to the login request; issued after only the password is verified, before the TOTP step; is already accepted as authenticated by every `/api/*` endpoint.

So after submitting just the password, the web UI correctly holds the browser at the TOTP screen (`/en/auth/2fa`), but the cookie from that same login response can be replayed against the API to act as the user without ever entering the second factor. This affects any account with 2FA enabled and requires only the account password.

### Details

#### Affected Component
- The API firewall / authorization.

`config/packages/security.yaml` guards the API with `{ path: '^/api', roles: IS_AUTHENTICATED }`. During 2FA the session carries a Scheb `TwoFactorToken`, which satisfies `IS_AUTHENTICATED` (it is a real, non-anonymous token). `App\API\Authentication\ApiRequestMatcher` returns `!$request->hasPreviousSession()`, so a request that carries the login session skips the stateless API firewall and is served by the main session firewall; Scheb's `TwoFactorAccessDecider::isAccessible()` then evaluates `IS_AUTHENTICATED` to true for `^/api` and lets it through, and `App\Voter\ApiVoter` grants `API` to any token whose user is a `User`. Web routes are not affected because they require concrete roles (e.g. `ROLE_USER`) that a `TwoFactorToken` does not hold.

### PoC

_A PoC was provided, but removed for security reasons._

### Impact

Two-factor authentication provides no protection for the REST API. If an attacker obtains a user's password (phishing, credential stuffing, reuse, breach); exactly the threat 2FA is meant to defend against; they get full authenticated API access as that user without the second factor. The whole exploit is a single cookie taken from the login response; no API token, Bearer header or CSRF token is required.

## Solution

- The `/api/` firewall now uses `IS_AUTHENTICATED_REMEMBERED` which is only assigned after 2FA. The historically used `IS_AUTHENTICATED` flag  is applied immediately after login and before 2FA happened.
- The APIVoter checks both `$token instanceof TwoFactorTokenInterface` and  `isGranted('IS_AUTHENTICATED_2FA_IN_PROGRESS', $user)` to make sure that the user is not currently in the  2FA step.
- Regression tests were added to prevent future escalation of the same issue.

See [https://www.kimai.org/en/security/ghsa-v8hx-4vx8-wc96](https://www.kimai.org/en/security/ghsa-v8hx-4vx8-wc96) for more information.

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-v8hx-4vx8-wc96
- https://github.com/kimai/kimai
