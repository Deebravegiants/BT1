# [M] Gogs's password-reset tokens use account-activation lifetime, ignoring RESET_PASSWORD_CODE_LIVES

## Summary
Severity: Medium
Advisory: GHSA-5c3f-6486-3g7g
CVE: CVE-2026-52809
CWE: CWE-324, CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-5c3f-6486-3g7g
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
## Summary

Password-reset tokens are generated using `conf.Auth.ActivateCodeLives` (the account-activation lifetime), not `conf.Auth.ResetPasswordCodeLives`. The token lifetime is baked into the token itself at generation time and is re-extracted from the token at verification time, making `RESET_PASSWORD_CODE_LIVES` irrelevant to actual enforcement. When an administrator configures a shorter reset window (e.g., 10 minutes) for compliance or security reasons, reset tokens remain exploitable for the full activation lifetime instead, while the reset email falsely advertises the shorter expiry.

## Severity

**Medium** (CVSS 3.1: 6.8)

`CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N`

- **Attack Vector:** Network — the reset endpoint is reachable over HTTP/S.
- **Attack Complexity:** High — successful exploitation requires (1) the instance to be configured with `RESET_PASSWORD_CODE_LIVES < ACTIVATE_CODE_LIVES`, AND (2) the attacker to have intercepted the victim's reset token (e.g., from a compromised or shared email inbox).
- **Privileges Required:** None — no Gogs account is required.
- **User Interaction:** Required — the victim must have triggered a password-reset request.
- **Scope:** Unchanged — the impact is confined to the victim's Gogs account.
- **Confidentiality Impact:** High — successful exploitation leads to account takeover, exposing all private repositories and data.
- **Integrity Impact:** High — the attacker can change the victim's password and gain full write access.
- **Availability Impact:** None.

## Affected component

- `internal/userx/userx.go` — `GenerateActivateCode()` (line 39)
- `internal/email/email.go` — `SendResetPasswordMail()` (line 132)
- `internal/route/user/auth.go` — `verifyUserActiveCode()` (lines 426–439) and `ResetPasswdPost()` (line 621)

## CWE

- **CWE-324**: Use of a Key Past Its Expiration Date
- **CWE-613**: Insufficient Session Expiration

## Description

### The reset token lifetime is hardcoded to `ActivateCodeLives` at generation

`GenerateActivateCode` (called for both account activation and password reset) bakes `conf.Auth.ActivateCodeLives` — not `ResetPasswordCodeLives` — into the token as a 6-digit field:

```go
// internal/userx/userx.go:36-46
func GenerateActivateCode(userID int64, email, name, password, rands string) string {
    code := tool.CreateTimeLimitCode(
        fmt.Sprintf("%d%s%s%s%s", userID, email, strings.ToLower(name), password, rands),
        conf.Auth.ActivateCodeLives,   // ← always ActivateCodeLives, never ResetPasswordCodeLives
        nil,
    )
    code += hex.EncodeToString([]byte(strings.ToLower(name)))
    return code
}
```

`CreateTimeLimitCode` embeds the `minutes` value at positions 12–17 of the token:

```
Token format: YYYYMMDDHHMM (12) | 000180 (6-digit lives) | SHA1 (40) | hex-username
```

`SendResetPasswordMail` calls `u.GenerateEmailActivateCode(u.Email())` — which resolves to `GenerateActivateCode` — with no option to pass a different lifetime:

```go
// internal/email/email.go:131-132
func SendResetPasswordMail(c *macaron.Context, u User) error {
    return SendUserMail(c, u, tmplAuthResetPassword, u.GenerateEmailActivateCode(u.Email()), ...)
}
```

### `ResetPasswordCodeLives` is used only for display, not enforcement

`VerifyTimeLimitCode` discards the `minutes` argument and re-extracts the lifetime directly from the token itself:

```go
// internal/tool/tool.go:62-86
func VerifyTimeLimitCode(data string, minutes int, code string) bool {
    start := code[:12]
    lives := code[12:18]
    if d, err := strconv.Atoi(lives); err == nil {
        minutes = d    // ← argument overridden by value baked into the token
    }
    retCode := CreateTimeLimitCode(data, minutes, start)
    if retCode == code && minutes > 0 {
        before, _ := time.ParseInLocation("200601021504", start, time.Local)
        if before.Add(time.Minute * time.Duration(minutes)).Unix() > now.Unix() {
            return true
        }
    }
    return false
}
```

The `verifyUserActiveCode` caller passes `conf.Auth.ActivateCodeLives` as `minutes`, but it makes no difference:

```go
// internal/route/user/auth.go:426-439
func verifyUserActiveCode(code string) (user *database.User) {
    minutes := conf.Auth.ActivateCodeLives   // passed to VerifyTimeLimitCode but immediately overridden
    if user = parseUserFromCode(code); user != nil {
        prefix := code[:tool.TimeLimitCodeLength]
        data := strconv.FormatInt(user.ID, 10) + user.Email + user.LowerName + user.Password + user.Rands
        if tool.VerifyTimeLimitCode(data, minutes, prefix) {
            return user
        }
    }
    return nil
}
```

`ResetPasswdPost` validates the reset token through `verifyUserActiveCode`, so it inherits the same flaw:

```go
// internal/route/user/auth.go:621
if u := verifyUserActiveCode(code); u != nil {
```

`ResetPasswordCodeLives` appears only in email template data and in the admin config display — it has zero effect on actual token validation:

```go
// internal/email/email.go:109 — template data only, not used to generate the token
"ResetPwdCodeLives": conf.Auth.ResetPasswordCodeLives / 60,
```

### Full execution chain

1. **Victim requests reset**: `POST /user/forget_password` → `SendResetPasswordMail` generates a token embedding `ActivateCodeLives = 180` at bytes 12–17.
2. **Email delivered**: The reset email says "link valid for 10 minutes" (from `ResetPwdCodeLives` in the template) but the embedded lifetime is 180.
3. **`RESET_PASSWORD_CODE_LIVES` window closes**: After 10 minutes the victim believes the link has expired.
4. **Attacker submits the token**: `POST /user/reset_password?code=<TOKEN>` → `ResetPasswdPost` → `verifyUserActiveCode` → `VerifyTimeLimitCode` extracts `000180` from the token → confirms the token has not yet reached the 180-minute mark → returns the user object → password is updated.
5. **Account takeover**: Attacker sets a new password and authenticates as the victim.

## Proof of Concept

```ini
# app.ini configuration that exposes the bug:
[auth]
ACTIVATE_CODE_LIVES = 180
RESET_PASSWORD_CODE_LIVES = 10
```

```bash
# 1) Request password reset for victim account
curl -i -X POST -d 'email=victim@example.com' http://HOST/user/forget_password

# 2) Obtain the reset link from the email.
#    Wait 11 minutes (past RESET_PASSWORD_CODE_LIVES, within ACTIVATE_CODE_LIVES).

# 3) Submit the "expired" reset code — it still succeeds
curl -i -X POST \
  -d 'code=<CODE_FROM_EMAIL>&password=AttackerNewPass' \
  'http://HOST/user/reset_password?code=<CODE_FROM_EMAIL>'

# Expected: HTTP 302 redirect to /user/login — password successfully changed
# despite the reset window having "closed" 10 minutes ago.
```

## Impact

- An administrator who sets `RESET_PASSWORD_CODE_LIVES` shorter than `ACTIVATE_CODE_LIVES` to limit the window of exposure for intercepted reset emails gets no security benefit from that configuration.
- Reset tokens remain valid for the full activation lifetime (default 3 hours), giving an attacker who has intercepted a reset email a much larger window to use it.
- The reset email actively misleads users by advertising a shorter expiry that is never enforced.
- All password-reset operations are affected; there is no per-user or per-request way to issue a correctly-expiring token.

## Recommended remediation

### Option 1: Add a `ResetPasswordCodeLives`-aware generation function (preferred)

Introduce a dedicated code-generation path that passes `conf.Auth.ResetPasswordCodeLives` instead of `ActivateCodeLives`:

```go
// internal/userx/userx.go
func GenerateResetPasswordCode(userID int64, email, name, password, rands string) string {
    code := tool.CreateTimeLimitCode(
        fmt.Sprintf("%d%s%s%s%s", userID, email, strings.ToLower(name), password, rands),
        conf.Auth.ResetPasswordCodeLives,   // ← correct lifetime
        nil,
    )
    code += hex.EncodeToString([]byte(strings.ToLower(name)))
    return code
}
```

Update `email.User` to expose this through the interface:

```go
// internal/email/email.go interface
GenerateResetPasswordCode(email string) string
```

Update `SendResetPasswordMail` to call it:

```go
func SendResetPasswordMail(c *macaron.Context, u User) error {
    return SendUserMail(c, u, tmplAuthResetPassword, u.GenerateResetPasswordCode(u.Email()), ...)
}
```

Because `VerifyTimeLimitCode` reads the lifetime from the token itself, no change to the verification side is required — tokens generated with `ResetPasswordCodeLives` will automatically expire at the correct time.

### Option 2: Validate the extracted lifetime against the configured maximum

Add a post-extraction check in `VerifyTimeLimitCode` or in the reset-specific verification function to reject tokens whose embedded lifetime exceeds `ResetPasswordCodeLives`:

```go
// in verifyUserActiveCode, after extracting the prefix:
embeddedLives := ... // parse positions 12-18 of the code
if embeddedLives > conf.Auth.ResetPasswordCodeLives {
    return nil  // reject tokens with a longer-than-allowed lifetime
}
```

This is a defence-in-depth measure but does not fix the root cause; Option 1 is preferred.

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-5c3f-6486-3g7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-52809
- https://github.com/gogs/gogs/pull/8328
- https://github.com/gogs/gogs/commit/187e9c557930eb4a8b9b1502ee45cccf3255ee7f
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
