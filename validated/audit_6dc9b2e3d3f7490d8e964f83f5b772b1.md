### Title
Uncontrolled Resource Consumption via Unbounded Password Length on Unauthenticated `/sessions` Login Endpoint - (File: core/web/sessions_controller.go)

### Summary
The unauthenticated `POST /sessions` login endpoint accepts an attacker-controlled JSON body and password field with no length limit, unlike every other password-accepting code path in the codebase which enforces `MaxBcryptPasswordLength = 50` and a 16–50 character complexity check before any expensive processing occurs.

### Finding Description
`SessionsController.Create` binds the raw HTTP request body directly into a `sessions.SessionRequest{}` via `c.ShouldBindJSON(&sr)` with no request body size limit (no `http.MaxBytesReader`/Gin body-limit middleware anywhere in `core/web`), and immediately forwards `sr.Password` to `sc.App.AuthenticationProvider().CreateSession(ctx, sr)`. [1](#0-0) 

For the local-auth provider, `CreateSession` calls `utils.CheckPasswordHash(sr.Password, string(user.HashedPassword))` directly on the unbounded, attacker-supplied password with no prior length check: [2](#0-1) 

`CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword`: [3](#0-2) 

The LDAP and OIDC providers' `TestPassword`/`localLoginFallback` login paths have the identical pattern — they compare the unbounded, unauthenticated-user-supplied password with `utils.CheckPasswordHash` with no length gate: [4](#0-3) [5](#0-4) 

This is inconsistent with every other password-handling path in the codebase. Both user creation and password-change explicitly reject overly long passwords before doing any hashing work: [6](#0-5) [7](#0-6) 

The route is only protected by a per-IP rate limiter, not by request size or password-length validation: [8](#0-7) 

### Impact Explanation
An unauthenticated network client can submit a login request with an arbitrarily large `password` field (e.g. multi-megabyte/gigabyte string) in the JSON body. Because there is no body-size cap and no length validation prior to JSON unmarshalling and the subsequent `bcrypt.CompareHashAndPassword` call, each such request forces the node to allocate memory proportional to the attacker-chosen payload size and perform password-hash comparison work on it. Repeated requests (bounded only by IP-based rate limiting, which does not limit payload size per request and can be trivially distributed across many source IPs/emails) can drive excessive memory/CPU consumption on a chainlink node's exposed web API, degrading availability — the same bug class as CVE-2023-25816 (uncontrolled resource consumption via long password on login).

### Likelihood Explanation
The `/sessions` endpoint is intentionally reachable pre-authentication (it is the login endpoint) and requires no credentials, valid email, or prior state — any network client that can reach the node's API can send oversized password payloads. The only mitigation present is IP-based rate limiting, which throttles request *count*, not request *size*, so a small number of large requests per rate-limit window can still consume disproportionate resources.

### Recommendation
Enforce a maximum request body size (e.g. `http.MaxBytesReader`/Gin body-limit middleware) on `/sessions` (and other unauthenticated endpoints), and add an explicit maximum password length check (mirroring `sessions.MaxBcryptPasswordLength`) in `SessionsController.Create` and in each `AuthenticationProvider.CreateSession`/`TestPassword` implementation (local, LDAP, OIDC) before performing JSON binding-heavy work or `CheckPasswordHash`/LDAP bind calls.

### Proof of Concept
1. Send `POST /sessions` with body `{"email":"victim@example.com","password":"<repeat 'a' 50-100MB times>"}` to an unauthenticated chainlink node API endpoint.
2. Observe that `SessionsController.Create` (`core/web/sessions_controller.go`) fully unmarshals the oversized body and forwards the password unchanged to `CreateSession`, which invokes `utils.CheckPasswordHash` (`core/utils/utils.go:131-135`) with no length rejection, unlike `sessions.ValidateAndHashPassword`'s explicit length check used on user creation/password-change paths.
3. Repeating the request (within/around the unauthenticated rate limit window defined in `core/web/router.go:207-213`) causes repeated large allocations/processing on the node.

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

**File:** core/utils/utils.go (L131-135)
```go
// CheckPasswordHash wraps around bcrypt.CompareHashAndPassword for a friendlier API.
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}
```

**File:** core/sessions/ldapauth/ldap.go (L620-642)
```go
}

// localLoginFallback tests the credentials provided against the 'local' authentication method
// This covers the case of local CLI API calls requiring local login separate from the LDAP server
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
}
```

**File:** core/sessions/oidcauth/oidc.go (L578-597)
```go
// localLoginFallback tests the credentials provided against the 'local' authentication method
// This covers the case of local CLI API calls requiring local login separate from the OIDC server
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
}
```

**File:** core/sessions/user.go (L68-76)
```go
// ValidateAndHashPassword is the single point of logic for user password validations
func ValidateAndHashPassword(plainPwd string) (string, error) {
	if err := utils.VerifyPasswordComplexity(plainPwd); err != nil {
		return "", pkgerrors.Wrapf(err, "password insufficiently complex:\n%s", utils.PasswordComplexityRequirements)
	}
	if len(plainPwd) > MaxBcryptPasswordLength {
		return "", pkgerrors.Errorf("must enter a password less than %v characters", MaxBcryptPasswordLength)
	}

```

**File:** core/utils/password.go (L44-70)
```go
func VerifyPasswordComplexity(password string, disallowedStrings ...string) (merr error) {
	errMsg := ErrMsgHeader
	var stringErrs []string

	if LeadingWhitespace.MatchString(password) || TrailingWhitespace.MatchString(password) {
		stringErrs = append(stringErrs, ErrWhitespace.Error())
	}

	if len(password) < MinRequiredLen {
		stringErrs = append(stringErrs, fmt.Sprintf("password is less than %d characters long", MinRequiredLen))
	}

	for _, s := range disallowedStrings {
		if strings.Contains(strings.ToLower(password), strings.ToLower(s)) {
			stringErrs = append(stringErrs, fmt.Sprintf("password may not contain: %q", s))
		}
	}

	if len(stringErrs) > 0 {
		for _, stringErr := range stringErrs {
			errMsg = fmt.Sprintf("%s	%s\n", errMsg, stringErr)
		}
		merr = errors.New(errMsg)
	}

	return
}
```

**File:** core/web/router.go (L207-218)
```go
func sessionRoutes(app chainlink.Application, r *gin.RouterGroup) {
	config := app.GetConfig()
	rl := config.WebServer().RateLimit()
	unauth := r.Group("/", rateLimiter(
		rl.UnauthenticatedPeriod(),
		rl.Unauthenticated(),
	))
	sc := NewSessionsController(app)
	unauth.POST("/sessions", sc.Create)
	auth := r.Group("/", auth.Authenticate(app.AuthenticationProvider(), auth.AuthenticateBySession))
	auth.DELETE("/sessions", sc.Destroy)
}
```
