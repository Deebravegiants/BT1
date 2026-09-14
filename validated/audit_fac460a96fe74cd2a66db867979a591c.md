Confirmed: `jsonAPIError` puts `err.Error()` directly into the JSON response body, so whatever error `CreateSession` returns is exposed verbatim to the unauthenticated client. [1](#0-0) 

### Title
User account enumeration via distinguishable login error messages - (File: core/web/sessions_controller.go)

### Summary
The unauthenticated `/sessions` login endpoint returns different, attacker-distinguishable error messages depending on whether the submitted email address corresponds to an existing Chainlink node user, allowing account enumeration analogous to CVE-2017-5537's password-reset enumeration in Weblate.

### Finding Description
`SessionsController.Create` binds an unauthenticated `SessionRequest` and forwards it to `CreateSession`, and on any failure it calls `jsonAPIError(c, http.StatusUnauthorized, err)`, which serializes `err.Error()` verbatim into the JSON response body. [2](#0-1) 

Inside `CreateSession`, the code first calls `o.FindUser(ctx, sr.Email)`, and if the email doesn't exist, it immediately returns the raw error from the database lookup (a `sql.ErrNoRows`-style error from `findUser`'s `GetContext` call) without any of the audit logging or generic wrapping applied further down. [3](#0-2) [4](#0-3) 

By contrast, when the email does exist but the password is wrong, the code returns a distinctly different, hardcoded error string, `pkgerrors.New("Invalid password")`. [5](#0-4) 

There is also a separate, further different error, `pkgerrors.New("Invalid email")`, returned from the constant-time email comparison branch. [6](#0-5) 

This produces at least three distinguishable response bodies for the same unauthenticated `/sessions` POST request depending on account state (nonexistent email → DB-driver-shaped "no rows" error text; existing email/wrong password → `"Invalid password"`; email-mismatch edge case → `"Invalid email"`), which lets an unauthenticated remote client enumerate valid node user accounts exactly as described in the Weblate advisory's bug class (different error messages leaking account existence).

### Impact Explanation
An unauthenticated attacker hitting the `/sessions` login endpoint can distinguish "this email is registered" from "this email is not registered" purely from the JSON error text, without needing valid credentials. This does not itself grant access, but it is a concrete confidentiality leak (CWE-200/CWE-209 analog) that materially aids further attacks such as targeted credential stuffing, phishing, or brute-forcing against confirmed Chainlink node operator accounts.

### Likelihood Explanation
High likelihood of exploitability: the endpoint is unauthenticated and internet-facing by design (login form), requires no special conditions, and the differing error text is returned deterministically on every request based solely on server-side email lookup success/failure.

### Recommendation
Return a single generic, identical error (e.g., `"invalid email or password"`) and identical HTTP status code (401) for all authentication failure paths in `CreateSession` (missing user, wrong password, and the email-mismatch branch), regardless of whether the email exists, and avoid propagating raw database/driver error text to the client via `jsonAPIError`.

### Proof of Concept
1. `POST /sessions` with `{"email":"realuser@example.com","password":"wrongpass"}` where `realuser@example.com` is a valid, existing node user → response body contains `"Invalid password"` (per `core/sessions/localauth/orm.go:159-162`).
2. `POST /sessions` with `{"email":"nonexistent@example.com","password":"wrongpass"}` where the email is not registered → response body contains a different error text originating from the raw SQL "no rows" lookup failure (per `core/sessions/localauth/orm.go:144-148` and `55-59`), returned via `jsonAPIError` in `core/web/sessions_controller.go:56-59`.
3. Comparing the two response bodies for the same HTTP status code (401) allows an attacker to determine which email addresses correspond to real accounts on the node.

### Citations

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

**File:** core/sessions/localauth/orm.go (L154-157)
```go
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
