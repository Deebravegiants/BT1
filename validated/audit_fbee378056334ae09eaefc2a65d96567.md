This confirms `jsonAPIError` writes `err.Error()` directly into the JSON response body regardless of message content, and `CreateSession` returns distinct error strings (`"Invalid email"` vs `"Invalid password"`) that propagate unmodified through `SessionsController.Create`. This is verified, real, currently-existing behavior in the code — not a fixed/mitigated issue. The claim is grounded in actual code (not speculative), reachable by any unauthenticated client via a normal POST to `/sessions`, and the impact (account-email enumeration) is a legitimate confidentiality-only information disclosure, matching the referenced CVE pattern.

Audit Report

## Title
Login Endpoint Reveals Account Existence Through Differential Error Messages - (File: core/sessions/localauth/orm.go)

## Summary
`SessionsController.Create` at `core/web/sessions_controller.go` forwards the raw error message returned by `AuthenticationProvider().CreateSession` directly to the client via `jsonAPIError`, which serializes `err.Error()` verbatim into the JSON response body. `CreateSession` in `core/sessions/localauth/orm.go` returns the distinct string `"Invalid email"` when the supplied email does not match a registered user, and `"Invalid password"` when the email is valid but the password is wrong — both under an identical `401` status code — allowing an unauthenticated attacker to enumerate registered account emails.

## Finding Description
The `Create` handler passes any `err` from `CreateSession` straight to `jsonAPIError(c, http.StatusUnauthorized, err)`: [1](#0-0) . `jsonAPIError` in turn calls `models.NewJSONAPIErrorsWith(err.Error())` when the error is not already a `*models.JSONAPIErrors`, embedding the raw message text into the JSON body sent to the client: [2](#0-1) .

In `orm.CreateSession`, the user is first resolved by email via `FindUser`; if that email doesn't match any registered account or otherwise fails to look up, its error is returned unmodified before the password branch is ever reached. Then explicit, distinct string literals are used for the email-mismatch and password-mismatch cases: `"Invalid email"` vs `"Invalid password"`: [3](#0-2) .

Both errors reach the client with the same `401` HTTP status but different message bodies, so an unauthenticated caller can distinguish "email unknown/not matching" from "email known, password wrong" purely by inspecting the JSON response text — no timing analysis, no privileged access, and no additional tooling required beyond scripted POST requests to `/sessions`. The LDAP and OIDC authenticator's `localLoginFallback` implementations follow the identical pattern with `"invalid email"` / `"invalid password"`: [4](#0-3) [5](#0-4) .

Notably, the code already implements a deliberate mitigation for a related leak in the same function — checking email/password before doing the WebAuthn/MFA lookup specifically "to prevent extra database look up for MFA tokens leaking if an account has MFA tokens or not," per the comment directly above the email check: [6](#0-5) . This confirms the team is aware of and actively mitigates enumeration-class leaks in this exact code path, but the email-vs-password message distinction itself was left unaddressed. No middleware, redaction layer, or generic-error wrapper exists between `CreateSession`'s error return and the HTTP response to normalize these messages.

## Impact Explanation
An unauthenticated attacker can enumerate valid API-user/node-operator email addresses on a Chainlink node by observing whether the `/sessions` login response body says `"Invalid email"` or `"Invalid password"`. This is a confidentiality-only information disclosure — it does not directly bypass authentication or move funds, but materially aids credential-stuffing, phishing, and targeted brute-force campaigns against a node's admin/API accounts, which control job runs, keys, and chain interactions.

## Likelihood Explanation
`/sessions` is an unauthenticated, internet-facing login endpoint by design, reachable with zero privileges. Exploitation requires only scripted POST requests with varying email guesses and inspection of the JSON error body — no advanced tooling or timing analysis needed — making likelihood high on any node lacking external rate-limiting.

## Recommendation
Return a single generic error (e.g., "invalid credentials") and status code for all authentication failure branches in `CreateSession` across the local, LDAP, and OIDC implementations, regardless of whether the failure occurred during email lookup, email comparison, or password check. Ensure `SessionsController.Create` never propagates internal, distinguishing error text to the HTTP response — wrap/replace the error before calling `jsonAPIError`. Consider extending the existing MFA-leak mitigation's design intent (avoiding differential internal signals) to also cover the `FindUser`-vs-password-check paths, and add uniform timing to avoid timing-based enumeration as a secondary hardening measure.

## Proof of Concept
1. `POST /sessions` with `{"email": "known-admin@example.com", "password": "wrong"}` → HTTP 401, body contains `"Invalid password"` (per `core/sessions/localauth/orm.go` line 161).
2. `POST /sessions` with `{"email": "nonexistent@example.com", "password": "wrong"}` → HTTP 401, body contains `"Invalid email"` (per `core/sessions/localauth/orm.go` line 156) — or the underlying `FindUser`/`sql.ErrNoRows`-derived message if the email lookup fails outright.
3. Both responses share the same status code; the message-text difference lets a script distinguish `"Invalid password"` from `"Invalid email"` across many candidate emails, confirming account-existence enumeration via `SessionsController.Create` → `jsonAPIError` → `err.Error()` serialization (`core/web/helpers.go` lines 21-29).

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L624-641)
```go
func (l *ldapAuthenticator) localLoginFallback(ctx context.Context, sr sessions.SessionRequest) (sessions.User, error) {
	var user sessions.User
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err := l.ds.GetContext(ctx, &user, sql, sr.Email)
	if err != nil {
		return user, err
	}
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		l.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		l.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}

	return user, nil
```

**File:** core/sessions/oidcauth/oidc.go (L580-596)
```go
func (oi *oidcAuthenticator) localLoginFallback(ctx context.Context, sr clsessions.SessionRequest) (clsessions.User, error) {
	var user clsessions.User
	err := oi.ds.GetContext(ctx, &user, SQLSelectUserbyEmail, sr.Email)
	if err != nil {
		return user, err
	}
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}

	return user, nil
```
