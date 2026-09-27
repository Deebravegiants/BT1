# [C] Note Mark has a JWT Secret Weakness that allows Full Account Takeover via Token Forgery

## Summary
Severity: Critical
Advisory: GHSA-q6mh-rqwh-g786
CVE: CVE-2026-44523
CWE: CWE-326, CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-q6mh-rqwh-g786
Type: github-advisory

## Affected
- Go: `github.com/enchant97/note-mark/backend` — affected >=0 <0.0.0-20260501152247-18b587758667

## Details
#### Summary

No minimum length or entropy is enforced on the `JWT_SECRET` configuration value. The application accepts any base64-decodable secret regardless of size, including secrets as short as 1 byte.

HS256 secrets below 32 bytes are brute-forceable offline, allowing attackers to recover the signing key and forge valid JWTs for arbitrary users.

---

#### Impact

An attacker who captures a single valid JWT (e.g, from cookies, logs, or network traffic) can:

\> Crack the signing secret offline using brute-force or wordlist attacks
\> Forge valid JWTs for any user ID (including administrators)
\> Authenticate without knowing any credentials

This results in **full account takeover across the entire application** with no server-side detection or rate limiting possible.

---

#### Details

In `backend/config/utils.go`, the `Base64Decoded.UnmarshalText` function decodes the JWT secret but does not validate its length or entropy.

In `backend/core/auth.go`, JWT tokens are signed using HS256 without enforcing minimum key size requirements.

According to **RFC 7518 Section 3.2**, HS256 keys must be at least 256 bits (32 bytes). Libraries such as PyJWT explicitly warn against shorter keys, but note-mark performs no such validation.

---

### PoC

1- Deploy note-mark with a weak secret:

   ```
   JWT_SECRET = base64("testsecret123456789012345")
   ```

2- Register an account and capture the `Auth-Session-Token` cookie

3- Crack the secret offline (example using Python):

   ```python
   import jwt, base64
   jwt.decode(TOKEN, base64.b64decode(SECRET), algorithms=["HS256"])
   ```

4- Forge a new token for any user UUID with extended expiry

5- Send the forged token in requests → server returns **200 Ok** and authenticates as that user

---

### Reproduction Steps

1- Deploy the application with a JWT secret shorter than 32 bytes (after base64 decoding)
2- Authenticate and capture a valid JWT
3- Perform offline brute-force or dictionary attack against the token signature
4- Recover the secret
5- Generate a forged JWT for another user
6- Use the forged token to access protected endpoints

---

### Fix Recommendation

* Enforce a **minimum of 32 bytes (256 bits)** for JWT secrets after base64 decoding
* Reject weak secrets during configuration parsing (e.g., in `Base64Decoded.UnmarshalText` or config validation)
* Optionally log warnings or fail startup if the secret is insecure

---

### Resources

* RFC 7518 Section 3.2 (JSON Web Algorithms - HMAC key size requirements)
* CWE-326: Inadequate Encryption Strength
* CWE-345: Insufficient Verification of Data Authenticity

---

## References
- https://github.com/enchant97/note-mark/security/advisories/GHSA-q6mh-rqwh-g786
- https://nvd.nist.gov/vuln/detail/CVE-2026-44523
- https://github.com/enchant97/note-mark/commit/18b58775866776ed400c403dd0ccad68c1fa4802
- https://github.com/enchant97/note-mark
- https://github.com/enchant97/note-mark/releases/tag/v0.19.4
