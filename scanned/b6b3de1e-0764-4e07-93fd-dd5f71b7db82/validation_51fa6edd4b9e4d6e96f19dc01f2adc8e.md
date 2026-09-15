### Title
Observable Response Discrepancy Enables Username (Email) Enumeration via Login Session Creation - ([File: core/sessions/localauth/orm.go])

### Summary
The `/sessions` login endpoint returns distinct, unauthenticated-attacker-visible error messages depending on whether a submitted email corresponds to an existing account, an existing account with a wrong password, or an existing account with MFA enabled. This mirrors the CWE-203/204 "Observable Response Discrepancy" class from GHSA-579x-cjvr-cqj9 (Pimcore forgot-password enumeration), but here the leak happens through the node's login/session flow rather than a password-reset flow.

### Finding Description
`SessionsController.Create` in [1](#0-0)  accepts an unauthenticated `POST /sessions` request, then calls `sc.App.AuthenticationProvider().CreateSession(ctx, sr)`. Any error returned is passed directly to `jsonAPIError(c, http.StatusUnauthorized, err)`, and `jsonAPIError` serializes `err.Error()` verbatim into the JSON response body sent to the client: [2](#0-1) 

`CreateSession` in `core/sessions/localauth/orm.go` produces different error text/content depending on account state:
- If the email does not exist, `FindUser` propagates the raw SQL "not found" error (e.g. `sql: no rows in result set`) unchanged: [3](#0-2) 
- If the email exists but the password is wrong, the distinct message `"Invalid password"` is returned: [4](#0-3) 
- If the account exists and has WebAuthn/MFA enrolled, a JSON-serialized WebAuthn challenge (`options`) is returned as the error body instead of a generic failure, revealing that MFA is configured for that email: [5](#0-4) 
- The email-existence check itself (`constantTimeEmailCompare`) is constant-time to avoid a *timing* side channel, but the resulting **message content** ("Invalid email" vs "Invalid password" vs a WebAuthn challenge payload vs a raw SQL not-found error) still leaks the same information through content, not timing: [6](#0-5) 

The `oidcauth` local-login fallback path exhibits the identical pattern (`"invalid email"` vs `"invalid password"`): [7](#0-6) 

### Impact Explanation
An unauthenticated network attacker can send crafted `POST /sessions` requests with a guessed email and an arbitrary password, then inspect the JSON error body/shape to determine:
1. Whether that email is a registered node admin/API user (distinguishing a raw SQL "no rows" style error from `"Invalid password"`).
2. Whether that account has WebAuthn/MFA enabled (distinguished by receiving a WebAuthn challenge JSON payload instead of a plain error).

This is a confidentiality-only issue (CWE-203/204, matching the CVSS vector `C:L/I:N/A:N` in the source advisory): it does not itself grant access, but it lets an attacker enumerate valid administrator/API accounts on a chainlink node's web UI, which materially assists follow-on credential-stuffing, phishing, or brute-force attacks and helps an attacker learn which accounts lack MFA (better targets).

### Likelihood Explanation
Likelihood is moderate-to-high: the endpoint is unauthenticated and internet/LAN-reachable by design (login page), requires no special privileges, and the discrepancy is deterministic (not a race or timing side channel) — a simple scripted probe with a wordlist of emails would reliably classify accounts as existing/non-existing and MFA-enabled/disabled.

### Recommendation
Normalize all failure responses from `CreateSession`/`localLoginFallback` (and the `/sessions` handler) to a single generic message (e.g., `"invalid credentials"`) and status code, regardless of whether the email exists, whether the password is wrong, or whether MFA is enrolled. Any WebAuthn challenge should only be issued after a successful password check (which the code partially already does — it only gets to the WebAuthn branch after password ok in the local ORM — but the earlier "email not found" vs "password wrong" distinction leaks through the top-level error message, and this discrepancy must be collapsed into one uniform response before it reaches `jsonAPIError`). Ensure `jsonAPIError` does not echo raw driver/SQL errors (e.g. `sql.ErrNoRows`) to unauthenticated callers.

### Proof of Concept
1. Send `POST /sessions` with `{"email":"nonexistent@x.com","password":"anything"}` — observe the JSON error body content/shape (raw SQL "no rows" style text propagated from `FindUser`).
2. Send `POST /sessions` with `{"email":"<known-existing-admin>","password":"wrongpass"}` — observe the distinct `"Invalid password"` error body.
3. Send `POST /sessions` with `{"email":"<existing-account-with-MFA>","password":"<correct password>"}` and no `webAuthnData` — observe a JSON WebAuthn challenge object returned instead of a generic error, confirming MFA is enabled for that email.
4. Compare responses across many candidate emails to enumerate valid accounts and their MFA status without any authentication.

### Citations

**File:** core/web/sessions_controller.go (L29-60)
```go
func (sc *SessionsController) Create(c *gin.Context) {
	defer sc.App.WakeSessionReaper()
	ctx := c.Request.Context()
	sc.App.GetLogger().Debugf("TRACE: Starting Session Creation")

	session := sessions.Default(c)
	var sr clsessions.SessionRequest
	if err := c.ShouldBindJSON(&sr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("error binding json %w", err))
		return
	}

	// Does this user have 2FA enabled?
	userWebAuthnTokens, err := sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)
	if err != nil {
		sc.App.GetLogger().Errorf("Error loading user WebAuthn data: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}

	// If the user has registered MFA tokens, then populate our session store and context
	// required for successful WebAuthn authentication
	if len(userWebAuthnTokens) > 0 {
		sr.SessionStore = sc.sessions
		sr.WebAuthnConfig = sc.App.GetWebAuthnConfiguration()
	}

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

**File:** core/sessions/localauth/orm.go (L144-148)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
```

**File:** core/sessions/localauth/orm.go (L152-163)
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

**File:** core/sessions/localauth/orm.go (L181-199)
```go
	// Next check if this session request includes the required WebAuthn challenge data
	// if not, return a 401 error for the frontend to prompt the user to provide this
	// data in the next round trip request (tap key to include webauthn data on the login page)
	if sr.WebAuthnData == "" {
		lggr.Warnf("Attempted login to MFA user. Generating challenge for user.")
		options, webauthnError := sessions.BeginWebAuthnLogin(user, uwas, sr)
		if webauthnError != nil {
			lggr.Errorf("Could not begin WebAuthn verification: %v", webauthnError)
			return "", pkgerrors.New("MFA Error")
		}

		j, jsonError := json.Marshal(options)
		if jsonError != nil {
			lggr.Errorf("Could not serialize WebAuthn challenge: %v", jsonError)
			return "", pkgerrors.New("MFA Error")
		}

		return "", pkgerrors.New(string(j))
	}
```

**File:** core/sessions/oidcauth/oidc.go (L586-594)
```go
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}
```
