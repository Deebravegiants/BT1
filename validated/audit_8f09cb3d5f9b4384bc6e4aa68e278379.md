This confirms a valid, unauthenticated user-enumeration analog in the `/sessions` login endpoint.

### Title
Unauthenticated user/email enumeration via distinct error messages on the `/sessions` login endpoint - (File: `core/web/sessions_controller.go`)

### Summary
The `POST /sessions` endpoint (`SessionsController.Create`) returns the raw, unmodified error string produced by `AuthenticationProvider().CreateSession` directly to the unauthenticated caller. Because `CreateSession` (local auth backend) produces different, distinguishable error messages depending on whether the submitted email exists in the `users` table versus whether the password was wrong, an unauthenticated attacker can enumerate valid Chainlink node operator/API-user email addresses by submitting login attempts and inspecting the returned error text — directly analogous to the PrestaShop `id_employee`/`reset_token` email-enumeration bug (CWE-203/CWE-359), except here the discrepancy is exposed via the authentication error body rather than a token/id parameter.

### Finding Description
`SessionsController.Create` binds the request and calls `CreateSession`, passing any resulting error straight to `jsonAPIError`, which serializes `err.Error()` into the JSON response body: [1](#0-0) [2](#0-1) 

In the local auth ORM, `CreateSession` first calls `FindUser`, which does a direct SQL lookup and returns the raw `sql.ErrNoRows` (or DB error) when the email doesn't exist — this error propagates unmodified up to the HTTP response. If the email does exist but the password is wrong, a different, explicit `"Invalid password"` error is returned instead: [3](#0-2) [4](#0-3) 

These two error paths are semantically and textually distinguishable ("sql: no rows in result set"-style message vs. `"Invalid password"`), letting an unauthenticated caller determine whether a given email is a registered node API user simply by observing which message is returned — a classic observable-discrepancy user-enumeration bug, the same bug class as the PrestaShop advisory (unauthenticated actor differentiates existing vs. non-existing accounts via endpoint responses).

Additionally, prior to `CreateSession`, the controller unconditionally calls `GetUserWebAuthn(ctx, sr.Email)` for any submitted email and returns a generic `500` only on a genuine DB error, not on "user not found" (which returns an empty, non-error list) — this call executes an unauthenticated DB query keyed purely on attacker-supplied email, further confirming that the endpoint treats unauthenticated email input as a valid identity-probing vector without rate limiting or generic error normalization: [5](#0-4) [6](#0-5) 

### Impact Explanation
An unauthenticated network attacker reaching a Chainlink node's back-office/API surface can enumerate valid administrator/API-user email addresses registered on that node. This information supports targeted phishing, credential-stuffing, and brute-force campaigns against real accounts, and reveals which emails have operator/admin access to a node that controls oracle jobs, keys, and potentially fund-moving transactions — matching the CVSS vector of the source advisory (`AC:H/PR:L/UI:N/S:U/C:L/I:L`), i.e., low direct impact but a meaningful confidentiality leak that facilitates further attacks.

### Likelihood Explanation
The `/sessions` endpoint is intentionally exposed for unauthenticated login (it exists specifically to authenticate previously-unauthenticated clients), so no special access is required. The differing error strings are deterministic and require no timing analysis — a single POST per candidate email is sufficient. Likelihood is high for any deployment where the admin/API HTTP interface is reachable by the attacker (as is assumed by the advisory's threat model for back-office URLs).

### Recommendation
- Normalize all `CreateSession` failure paths (`user not found`, `invalid email`, `invalid password`, `MFA error`) to a single generic, non-distinguishing message (e.g., `"invalid credentials"`) before returning via `jsonAPIError`, both for the local, LDAP, and OIDC authenticators.
- Do not leak raw SQL/driver errors (`sql.ErrNoRows`, etc.) from `FindUser`/`CreateSession` to the HTTP layer; wrap and mask them centrally in `SessionsController.Create`.
- Apply constant-time/constant-work behavior (e.g., always perform a dummy password hash comparison) even when the user is not found, to avoid timing-based enumeration as a secondary channel.
- Add rate limiting / backoff on the `/sessions` endpoint keyed by source IP and/or submitted email to blunt enumeration attempts regardless of message normalization.

### Proof of Concept
1. `POST /sessions` with `{"email":"known-admin@node.com","password":"wrong"}` → response body contains `"Invalid password"`.
2. `POST /sessions` with `{"email":"nonexistent@node.com","password":"wrong"}` → response body contains a distinct DB-level error (e.g., `"sql: no rows in result set"`), because `FindUser` fails before any password check is attempted: [7](#0-6) 
3. By scripting step 1/2 against a candidate email list and diffing the two response bodies, an unauthenticated attacker builds a list of confirmed valid node API-user emails.

### Citations

**File:** core/web/sessions_controller.go (L41-47)
```go
	// Does this user have 2FA enabled?
	userWebAuthnTokens, err := sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)
	if err != nil {
		sc.App.GetLogger().Errorf("Error loading user WebAuthn data: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}
```

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/web/helpers.go (L21-29)
```go
func jsonAPIError(c *gin.Context, statusCode int, err error) {
	_ = c.Error(err).SetType(gin.ErrorTypePublic)
	var jsonErr *models.JSONAPIErrors
	if errors.As(err, &jsonErr) {
		c.JSON(statusCode, jsonErr)
		return
	}
	c.JSON(statusCode, models.NewJSONAPIErrorsWith(err.Error()))
}
```

**File:** core/sessions/localauth/orm.go (L55-59)
```go
func (o *orm) findUser(ctx context.Context, email string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err = o.ds.GetContext(ctx, &user, sql, email)
	return
}
```

**File:** core/sessions/localauth/orm.go (L130-139)
```go
func (o *orm) GetUserWebAuthn(ctx context.Context, email string) ([]sessions.WebAuthn, error) {
	var uwas []sessions.WebAuthn
	err := o.ds.SelectContext(ctx, &uwas, "SELECT email, public_key_data FROM web_authns WHERE LOWER(email) = $1", strings.ToLower(email))
	if err != nil {
		return uwas, err
	}
	// In the event of not found, there is no MFA on this account and it is not an error
	// so this returns either an empty list or list of WebAuthn rows
	return uwas, nil
}
```

**File:** core/sessions/localauth/orm.go (L144-162)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	lggr := o.lggr.With("user", user.Email)
	lggr.Debugw("Found user")

	// Do email and password check first to prevent extra database look up
	// for MFA tokens leaking if an account has MFA tokens or not.
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		o.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```
