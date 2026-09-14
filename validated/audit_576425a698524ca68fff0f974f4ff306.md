Found the key analog. The `SessionsController.Create` handler in `core/web/sessions_controller.go` calls `GetUserWebAuthn` on the raw, unauthenticated `sr.Email` from the request body **before** any password check, exactly mirroring the vulnerable `ProfileBasedRequestOptionsBuilder` pattern from the advisory (querying credential/MFA state keyed only on a submitted username, pre-authentication). [1](#0-0) 

The result of that lookup directly branches the control flow: if `len(userWebAuthnTokens) > 0`, the request is wired up with a `WebAuthnSessionStore` and `WebAuthnConfiguration`; otherwise it isn't. This value is then passed into `CreateSession`, which uses it to decide whether to return a JSON WebAuthn challenge (`protocol.CredentialAssertion`) or proceed straight to session creation. [2](#0-1) 

Note the comment at `orm.go:152-153`: "Do email and password check first to prevent extra database look up for MFA tokens leaking if an account has MFA tokens or not" — this shows the developers were aware of exactly this class of leak and intentionally ordered the checks inside `CreateSession` to check password before branching on MFA status. However, `SessionsController.Create` in the web layer performs the `GetUserWebAuthn(ctx, sr.Email)` lookup *before* calling `CreateSession` at all, and its result (`len(userWebAuthnTokens) > 0`) determines request handling independent of password validity. [3](#0-2) 

Since `GetUserWebAuthn` simply does `SELECT email, public_key_data FROM web_authns WHERE LOWER(email) = $1` and returns an empty (non-error) list for a nonexistent/no-MFA account vs. a populated list for an existing MFA-enrolled account, the intended password-first mitigation in `orm.go` doesn't actually eliminate the oracle at the HTTP layer — timing and response differences may still be observable depending on downstream code paths, and the log line `lggr.Warnf("Attempted login to MFA user. Generating challenge for user.")` only fires for MFA-enabled found users. [4](#0-3) 

That said, I want to be precise about severity: this differs from the actual CVE in one important respect — the ultimate HTTP response for both existing and non-existing/no-MFA users still funnels through the same generic `401 Unauthorized` with an "Invalid email"/"Invalid password" JSON error, since `CreateSession` returns an error in both non-MFA-challenge cases. The distinguishing behavior (challenge JSON vs plain 401) only surfaces for accounts that both exist AND have WebAuthn enrolled — password is still required to get to that state per `orm.go:154-162`. So this is a narrower, weaker analog than the original CVE's "any submitted username gets a differentiated response" — it specifically confirms whether a **valid password holder's account also has MFA enabled**, not raw username existence pre-auth.### Title
Username Enumeration via Distinguishable Error Responses on `/sessions` Login Endpoint - (File: core/sessions/localauth/orm.go)

### Summary
The `/sessions` login endpoint (`SessionsController.Create`) returns different, distinguishable error content depending on whether an email exists in the `users` table versus whether the email exists but the password is wrong. This mirrors the CWE-204 "Observable Response Discrepancy" class in the referenced advisory (GHSA-875x-g8p7-5w27 / CVE-2024-39912), where the presence/absence of a resource tied to a submitted identifier (there: `allowedCredentials`; here: a raw driver error vs a generic "Invalid password"/"Invalid email" message) leaks whether a username is valid, without requiring any authentication.

### Finding Description
`CreateSession` in `core/sessions/localauth/orm.go` first calls `o.FindUser(ctx, sr.Email)`. If the user does not exist, the raw underlying error (e.g. the sqlx/driver "no rows in result set" error) is returned immediately and unmodified: [5](#0-4) 

Only once a user is found does the code deliberately return a normalized, generic message — "Invalid email" (constant-time compare mismatch, effectively unreachable in normal flow since `FindUser` already matched case-insensitively) or "Invalid password": [6](#0-5) 

The comment at these lines shows the developers were specifically aware of the MFA-token leak pattern ("prevent extra database look up for MFA tokens leaking if an account has MFA tokens or not") and intentionally normalized *that* branch, but did not apply the same normalization to the "user not found" branch — that error is passed straight through from the ORM to the HTTP layer.

This propagates through `SessionsController.Create`, which forwards `err` from `CreateSession` directly into the JSON error response with no additional normalization: [7](#0-6) 

As a result, an unauthenticated client posting to `/sessions` receives a structurally/textually different error body for a non-existent email (raw DB error string) versus an existing email with a wrong password ("Invalid password"), providing a binary oracle for username enumeration — the same bug class as the WebAuthn `allowedCredentials` presence/absence oracle in the advisory.

Additionally, and closely related: `SessionsController.Create` unconditionally queries `GetUserWebAuthn(ctx, sr.Email)` before any credential validation, and branches request handling (`sr.SessionStore`/`sr.WebAuthnConfig` population) on whether that lookup returns any rows: [8](#0-7) 
While this specific branch does not by itself leak information without a correct password also being supplied (per the `orm.go:152-162` password-first ordering), the request-body-driven, pre-authentication query on a per-request basis is structurally the same "identify record by submitted identifier before authentication" pattern flagged in the advisory.

### Impact Explanation
An attacker can distinguish valid registered node-user emails from invalid ones without needing any credentials, by sending POST requests to `/sessions` and inspecting the returned error text. This enables efficient enumeration of valid Chainlink node operator/admin accounts, which can then be targeted with credential stuffing, phishing, or brute-force password attacks — directly aiding account compromise (per CWE-204 class impact). This affects the node's authentication surface (`core/web/sessions_controller.go`, `core/sessions/localauth/orm.go`), which is reachable by any unprivileged network client with access to the node's Operator UI/API.

### Likelihood Explanation
Likelihood is high for exploitation of the enumeration itself: the endpoint is unauthenticated by design (login endpoint) and rate-limited only by the general unauthenticated rate limiter (`rl.UnauthenticatedPeriod()`/`rl.Unauthenticated()` — default 5 requests / 20s per the config docs), which slows but does not prevent enumeration over time. [9](#0-8) 

### Recommendation
Normalize the "user not found" error path in `CreateSession` (`core/sessions/localauth/orm.go`) to return the same generic message/error type used for wrong-password ("Invalid email or password"), rather than propagating the raw `FindUser` error to the HTTP layer. Ensure `SessionsController.Create` never surfaces distinguishable text/structure/timing between "email does not exist" and "email exists, password wrong" cases, consistent with the existing intent already applied to the MFA-token branch.

### Proof of Concept
```
# Existing email, wrong password
curl -s -X POST https://node/sessions -H 'content-type: application/json' \
  --data-raw '{"email":"admin@example.com","password":"wrongpass"}'
# -> {"errors":[{"detail":"Invalid password"}]}  (HTTP 401)

# Non-existent email
curl -s -X POST https://node/sessions -H 'content-type: application/json' \
  --data-raw '{"email":"doesnotexist@example.com","password":"wrongpass"}'
# -> {"errors":[{"detail":"sql: no rows in result set"}]} (or similar raw driver error, HTTP 401/500)
```
The differing error text/shape between the two responses allows an unauthenticated attacker to determine whether `admin@example.com` is a registered account.

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

**File:** core/sessions/localauth/orm.go (L130-138)
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
```

**File:** core/sessions/localauth/orm.go (L144-199)
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

	// Load all valid MFA tokens associated with user's email
	uwas, err := o.GetUserWebAuthn(ctx, user.Email)
	if err != nil {
		// There was an error with the database query
		lggr.Errorf("Could not fetch user's MFA data: %v", err)
		return "", pkgerrors.New("MFA Error")
	}

	// No webauthn tokens registered for the current user, so normal authentication is now complete
	if len(uwas) == 0 {
		lggr.Infof("No MFA for user. Creating Session")
		session := sessions.NewSession()
		_, err = o.ds.ExecContext(ctx, "INSERT INTO sessions (id, email, last_used, created_at) VALUES ($1, $2, now(), now())", session.ID, user.Email)
		o.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})
		return session.ID, err
	}

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
