### Title
Local-auth login endpoint leaks raw database errors, enabling user/email enumeration - (File: `core/web/sessions_controller.go`, `core/sessions/localauth/orm.go`)

### Summary
The `POST /sessions` login endpoint returns the raw, unwrapped error from `AuthenticationProvider().CreateSession` directly to the unauthenticated caller. Because the underlying local-auth implementation returns different, distinguishable error strings depending on whether the supplied email exists in the `users` table versus whether the password is wrong, an unauthenticated attacker can enumerate valid Chainlink node user accounts by observing the returned error text — the same class of bug as CVE-2022-40084 (OpenCRX password-reset enumeration via distinguishable error messages, CWE-203).

### Finding Description
`SessionsController.Create` forwards the login request to the authentication provider and, on any failure, echoes the raw error straight into the JSON response body: [1](#0-0) 

`jsonAPIError` puts `err.Error()` verbatim into the `detail` field of the JSON:API error response that is sent back to the client: [2](#0-1) 

The local authentication provider's `CreateSession` produces three distinguishable outcomes:
1. Email not present → `FindUser`/`findUser` executes `SELECT * FROM users WHERE lower(email) = lower($1)` via `sqlx.GetContext`, which returns the driver's `sql: no rows in result set` error, propagated unmodified.
2. Email present but case-mismatch/canonicalization edge case → `"Invalid email"`.
3. Email present but wrong password → `"Invalid password"`. [3](#0-2) [4](#0-3) 

Because these three distinct error strings are all returned to the caller unchanged, an attacker submitting a login request can determine whether a given email is a registered node user simply by inspecting the returned error text: `sql: no rows in result set` reveals "email does not exist" while `Invalid password` reveals "email exists, password wrong."

### Impact Explanation
This is an unauthenticated, internet-reachable oracle for enumerating valid Chainlink Node Operator UI/API accounts (admin, edit, run, view roles). Knowledge of valid account emails materially assists follow-on credential-stuffing or targeted brute-force attacks against the node's admin API, which controls job specs, keys, and on-chain fund-moving operations. Confidentiality impact is limited to account existence disclosure (mirrors the Low/C:L rating of the original CVE), with no direct authentication bypass by itself.

### Likelihood Explanation
High likelihood of exploitability: the `/sessions` endpoint requires no prior authentication, requests are cheap, and the differing error text is deterministic and unthrottled at the application layer, making automated enumeration straightforward for any attacker able to reach the node's web/API port.

### Recommendation
Normalize all `CreateSession` failure paths in `core/sessions/localauth/orm.go` (and the LDAP/OIDC equivalents that exhibit the same pattern in `core/sessions/ldapauth/ldap.go` and `core/sessions/oidcauth/oidc.go`) to return one generic error (e.g., `"invalid email or password"`) regardless of whether the email lookup failed or the password check failed, and avoid propagating raw driver errors (`sql.ErrNoRows`) to `jsonAPIError`. Ensure timing is also constant-time between the "user not found" and "wrong password" branches to avoid a timing side channel.

### Proof of Concept
1. `POST /sessions` with `{"email":"nonexistent@example.com","password":"anything"}` → response body contains `sql: no rows in result set`.
2. `POST /sessions` with `{"email":"<real-admin-email>","password":"wrongpass"}` → response body contains `Invalid password`.
3. Comparing the two distinct response bodies across a list of candidate emails lets an attacker confirm which emails correspond to real accounts on the node without any authentication.

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/web/helpers.go (L19-29)
```go
// jsonAPIError adds an error to the gin context and sets
// the JSON value of errors.
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
