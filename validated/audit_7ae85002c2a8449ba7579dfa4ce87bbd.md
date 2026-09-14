### Title
Login endpoint returns raw sql/"no rows" error when email doesn't exist, enabling email enumeration - (File: core/web/sessions_controller.go)

### Summary
Chainlink has no "forgot password" email flow analogous to Statamic's, but the `/sessions` login endpoint (`SessionsController.Create`) exhibits the same bug class: it returns a raw, distinguishable error message to an unauthenticated caller depending on whether the submitted email corresponds to an existing user, letting an attacker enumerate valid Chainlink node operator accounts.

### Finding Description
`SessionsController.Create` passes whatever error `CreateSession` returns directly back to the client as the HTTP body via `jsonAPIError(c, http.StatusUnauthorized, err)`: [1](#0-0) 

Inside `orm.CreateSession`, the very first step calls `FindUser`, and if the email doesn't exist in the `users` table, the underlying database "no rows" error (from `sqlutil` `GetContext`) is returned unmodified: [2](#0-1) 

If the email *does* exist but the password is wrong, a different, distinct error string, `"Invalid password"`, is returned instead: [3](#0-2) 

There's also a separate `"Invalid email"` branch for a case-mismatch check that only triggers once a user row was already found by case-insensitive lookup: [4](#0-3) 

Because these three distinct error paths (DB "no rows" error / "Invalid password" / MFA challenge JSON) are all propagated verbatim to the HTTP response body via `jsonAPIError(c, http.StatusUnauthorized, err)`, an unauthenticated client submitting different emails to `POST /sessions` gets different, distinguishable response bodies depending on whether the email is registered — the exact bug class described in the Statamic advisory (response content reveals account existence).

### Impact Explanation
An unauthenticated attacker can enumerate valid operator/admin email addresses on a Chainlink node's web/API by observing whether the login response contains a generic SQL "no rows" style error (email not found) versus `"Invalid password"` (email found, wrong password) versus an MFA challenge payload (email found, MFA enabled). This does not itself grant access, but it materially aids follow-up credential-stuffing/brute-force/social-engineering/phishing attacks against confirmed valid accounts, matching CWE-204 (Observable Response Discrepancy) and the low-confidentiality-impact CVSS profile of the referenced advisory (C:L/I:N/A:N).

### Likelihood Explanation
High likelihood of exploitability: the endpoint is unauthenticated, internet-facing (or LAN-facing depending on deployment), requires no special privileges, and simply differing response bodies/timing based on a single JSON POST to `/sessions` is trivial to script and does not require rate-limit bypass beyond normal automation.

### Recommendation
Return a single generic, constant error message and HTTP status (e.g., always `401 Unauthorized: "invalid email or password"`) from `SessionsController.Create` regardless of whether the email exists, the password is wrong, or MFA state differs, mirroring the Statamic fix. Avoid propagating raw ORM/database errors (`err` from `FindUser`/`CreateSession`) directly into the HTTP response; wrap and normalize them in the controller before calling `jsonAPIError`. Ensure the MFA-challenge branch does not leak account existence either (e.g., issue a WebAuthn-style challenge to non-existent accounts too, or unify timing/response shape).

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@node.example","password":"x"}` → response contains a driver-level "no rows" style error (email not found in `users` table), sourced from: [2](#0-1) 
2. `POST /sessions` with `{"email":"knownadmin@node.example","password":"wrongpass"}` (using a known/registered admin email) → response instead contains `"Invalid password"`: [3](#0-2) 
3. Both bodies are returned verbatim to the client at status 401 via: [1](#0-0) 
4. Diffing these two response bodies across a wordlist of candidate emails lets an attacker confirm which emails correspond to real Chainlink node operator accounts.

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/sessions/localauth/orm.go (L144-148)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
```

**File:** core/sessions/localauth/orm.go (L152-157)
```go
	// Do email and password check first to prevent extra database look up
	// for MFA tokens leaking if an account has MFA tokens or not.
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		o.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid email")
	}
```

**File:** core/sessions/localauth/orm.go (L159-162)
```go
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```
