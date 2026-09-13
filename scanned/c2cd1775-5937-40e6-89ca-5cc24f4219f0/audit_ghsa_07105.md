# [H] Pterodactyl's shared global rate-limit key on login and 2FA checkpoint enables unauthenticated panel-wide authentication lockout (DoS)

## Summary
Severity: High
Advisory: GHSA-xvc3-826v-xf47
CVE: CVE-2026-61609
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-xvc3-826v-xf47
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=1.7.0 <1.13.0

## Details
### Summary
The `authentication` rate limiter used for the login and two-factor checkpoint endpoints applies a single global bucket shared by every client, instead of keying per IP or per account. An unauthenticated attacker sending ~10 requests per minute from one IP exhausts the shared bucket and causes HTTP 429 for every user on every IP attempting to log in or complete 2FA, for as long as the attack is sustained. This is a trivially triggered, unauthenticated, panel-wide authentication denial of service.

### Details
In `app/Providers/RouteServiceProvider::configureRateLimiting()` the limiter is defined as:

```php
RateLimiter::for('authentication', function (Request $request) {
    if ($request->route()->named('auth.post.forgot-password')) {
        return Limit::perMinute(2)->by($request->ip());
    }

    return Limit::perMinute(10);
});
```

The forgot-password branch is correctly scoped with `->by($request->ip())`. The fall-through return, which covers `POST /auth/login` and `POST /auth/login/checkpoint` (see `routes/auth.php`, the `throttle:authentication` group), omits `->by()` entirely.

For a named limiter, Laravel 11 derives the cache key as `md5($limiterName . $limit->key)` (`Illuminate\Routing\Middleware\ThrottleRequests::handleRequestUsingNamedLimiter`). `Limit::perMinute(10)` is constructed with an empty `key`, so the resolved key is `md5('authentication')`, a constant identical for every incoming request. All clients therefore contend for one shared counter rather than one counter per source.

Two factors make this worse:
- `throttle:authentication` is registered as group middleware in `routes/auth.php`, so it increments before the route-level `recaptcha` middleware on `POST /auth/login`. Requests count toward the limit regardless of reCAPTCHA outcome.
- `POST /auth/login/checkpoint` has no reCAPTCHA at all, giving an attacker a clean, low-cost way to fill the shared bucket with malformed requests.

Once the 10/minute global limit is hit, the throttle returns 429 to all subsequent requests on those endpoints until the one-minute window decays. Repeating the burst each minute holds the panel in a permanent locked-out state for all legitimate users.

### PoC
1. Stand up a default Pterodactyl panel.
2. From a single attacker IP, exhaust the shared bucket via the checkpoint endpoint (no reCAPTCHA):

```bash
for i in $(seq 1 11); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST https://panel.example.com/auth/login/checkpoint \
    -H 'Content-Type: application/json' \
    -H 'X-Requested-With: XMLHttpRequest' \
    -d '{"confirmation_token":"x","authentication_code":"000000"}'
done
```

Requests 1-10 return a normal 4xx (validation/auth failure); request 11 returns `429 Too Many Requests`.

3. From a completely different IP and a valid account, attempt a normal login:

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST https://panel.example.com/auth/login \
  -H 'Content-Type: application/json' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -d '{"user":"valid@example.com","password":"correct-horse"}'
```

This returns `429` despite being a different IP, different account, and valid credentials. Looping step 2 once per minute keeps every user locked out indefinitely.

### Impact
This is an unauthenticated availability attack against authentication. Any internet-facing Pterodactyl panel can be made unusable for all users (login and 2FA verification both blocked) by a single low-bandwidth attacker, with no credentials, no privileges, and no user interaction. Administrators are locked out alongside regular users, hampering incident response. The forgot-password endpoint is unaffected because it is correctly keyed per IP.

Suggested fix: key the fall-through limit by request source, at minimum:

```php
return Limit::perMinute(10)->by($request->ip());
```

Ideally combine the IP with the submitted identifier for login (e.g. `->by($request->ip() . '|' . (string) $request->input('user'))`) and the IP plus confirmation token for the checkpoint, so brute-force protection per account is preserved while removing the shared global bucket.

### Disclaimer
This report was written by AI, the bug itself was found and confirmed by the reporter.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-xvc3-826v-xf47
- https://github.com/pterodactyl/panel
