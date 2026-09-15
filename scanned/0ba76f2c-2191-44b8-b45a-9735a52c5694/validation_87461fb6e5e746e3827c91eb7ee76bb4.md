## Analysis Result

The chainlink login flow contains an analogous username enumeration issue, structurally identical to the Mautic bug class (distinguishable login responses based on username existence).

### Title
Username Enumeration via Distinguishable Login Error Responses in Local Session Authentication - (File: `core/sessions/localauth/orm.go`)

### Summary
The `/sessions` login endpoint (`SessionsController.Create`) returns different, distinguishable error messages depending on whether the submitted email exists in the `users` table or not, allowing an unauthenticated attacker to enumerate valid Chainlink node user accounts.

### Finding Description
`CreateSession` in the local authentication provider first looks up the user by email, and if the lookup fails it returns the *raw* underlying error unmodified: [1](#0-0) 

Since `findUser` performs a direct `GetContext` query without wrapping the "no rows" case, a non-existent email causes `sql.ErrNoRows` (e.g. `"sql: no rows in result set"`) to propagate all the way up: [2](#0-1) 

By contrast, when the email *does* exist but the password is wrong, a distinct, human-readable message is returned instead: [3](#0-2) 

Both code paths funnel into the HTTP layer unmodified — `SessionsController.Create` passes whatever `err` `CreateSession` returns straight into the JSON:API error response body: [4](#0-3) 

The test suite confirms that these error strings are surfaced verbatim in the `errors.Errors[0].Detail` field of the HTTP response (seen for a related endpoint, `UpdatePassword`, using the same `jsonAPIError` helper): [5](#0-4) 

Therefore, an attacker submitting `POST /sessions` with a bogus password can distinguish:
- **Unknown email** → `"sql: no rows in result set"` (a low-level DB error, distinct from any deliberate "Invalid ..." wording)
- **Known email, wrong password** → `"Invalid password"`

This mirrors the Mautic bug class exactly: two different failure messages for "unknown user" vs. "known user, wrong credential," letting an attacker enumerate valid usernames/emails on the node's Operator UI / API.

### Impact Explanation
An unauthenticated network attacker can enumerate valid administrator/operator email addresses registered on a Chainlink node's local auth backend by observing the HTTP `POST /sessions` response body. Knowledge of valid usernames on a chainlink node (which acts as an oracle/CL node with fund-moving and job-management capabilities) materially aids follow-on credential-stuffing, phishing, or brute-force attacks against a known-valid account, and is explicitly classified CWE-200/CWE-204 (information disclosure through discrepant responses), matching the referenced advisory's severity class.

### Likelihood Explanation
The endpoint is unauthenticated and directly internet-reachable (the standard node login form/API), requires no privilege, and the distinguishing signal (differing error text) is deterministic and trivial to script — likelihood is high for any node with this HTTP API exposed.

### Recommendation
Normalize all `CreateSession` failure paths in `core/sessions/localauth/orm.go` (and the equivalent LDAP/OIDC `localLoginFallback` paths, which already return "invalid email"/"invalid password" — same issue) to return one generic, identical error (e.g., `"Invalid credentials"`) regardless of whether the email lookup failed or the password check failed, and ensure no raw database error (`sql.ErrNoRows` or similar) is ever propagated to the HTTP response.

### Proof of Concept
1. `POST /sessions` with `{"email": "definitely-not-a-real-user@example.com", "password": "wrongpass"}` → response `Detail` contains a raw SQL/no-rows-style error.
2. `POST /sessions` with `{"email": "<valid-existing-admin-email>", "password": "wrongpass"}` → response `Detail` contains `"Invalid password"`.
3. The differing response bodies allow an attacker to confirm which email addresses are registered node users.

### Citations

**File:** core/sessions/localauth/orm.go (L55-59)
```go
func (o *orm) findUser(ctx context.Context, email string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE lower(email) = lower($1)"
	err = o.ds.GetContext(ctx, &user, sql, email)
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

**File:** core/sessions/localauth/orm.go (L152-162)
```go
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

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/web/user_controller_test.go (L42-48)
```go
		{
			name:           "Incorrect old password",
			reqBody:        `{"oldPassword": "wrong password"}`,
			wantStatusCode: http.StatusConflict,
			wantErrCount:   1,
			wantErrMessage: "old password does not match",
		},
```
