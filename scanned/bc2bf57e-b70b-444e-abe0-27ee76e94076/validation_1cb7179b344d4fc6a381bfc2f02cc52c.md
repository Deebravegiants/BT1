### Title
Username Enumeration via Timing Side-Channel in Local Login (`CreateSession`) - (File: `core/sessions/localauth/orm.go`)

### Summary
The unauthenticated `POST /sessions` endpoint calls `AuthenticationProvider().CreateSession`, which performs a fast-fail database lookup for nonexistent emails but an expensive bcrypt comparison for existing ones — the same bug class as CVE-2026-44255 in Wazuh's `AuthenticationManager.check_user()`.

### Finding Description
`SessionsController.Create` binds the request body directly to `sessions.SessionRequest` and forwards it, unauthenticated, to `AuthenticationProvider().CreateSession`: [1](#0-0) 

In the local auth provider, `CreateSession` first calls `FindUser`, and if the email does not exist in the database it returns the error immediately — no bcrypt work is ever performed. Only when the user record is found does the code proceed to `constantTimeEmailCompare` and the expensive `utils.CheckPasswordHash` (bcrypt) call: [2](#0-1) 

`CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword`, which is deliberately slow (tunable cost factor), unlike a DB row-not-found lookup: [3](#0-2) 

This exact asymmetry — "return fast if user doesn't exist, otherwise do slow bcrypt" — is precisely the pattern described in the Wazuh advisory. The same pattern is duplicated in the LDAP and OIDC local-fallback paths as well (`localLoginFallback` in `core/sessions/ldapauth/ldap.go:624-642` and `core/sessions/oidcauth/oidc.go:580-597`), though those still hit an upstream directory/IdP call first in the primary path; the pure local-auth provider is the cleanest, most directly reachable instance since `/sessions` is the only auth backend for many deployments (non-LDAP/non-OIDC nodes) and is fully unauthenticated.

The route is registered under an unauthenticated rate-limited group: [4](#0-3) 

### Impact Explanation
An unauthenticated remote attacker can distinguish "email exists" (slow bcrypt path) from "email does not exist" (fast DB-miss path) by measuring response latency of repeated `POST /sessions` requests. This enables enumeration of valid Chainlink node operator/admin email addresses, which can then be used to focus credential-stuffing or brute-force attacks against real accounts, or to map organizational structure (email addresses) tied to a sensitive infrastructure control plane (the node's admin API can move funds, manage jobs, and rotate keys). This matches "authentication bypass primitives" / "cross-user response confusion" in spirit — it's a precursor enabling more effective account-takeover attempts rather than a direct compromise.

### Likelihood Explanation
The endpoint is public and unauthenticated, protected only by generic rate limiting (`rl.UnauthenticatedPeriod()`), which does not defend against timing analysis — an attacker can average many samples over time within rate limits to reduce noise, and rate limiting itself doesn't equalize response time. The bug is directly reachable with a single crafted JSON body (`{"email":..., "password":...}`) at `/sessions`, no special network position or privileges required.

### Recommendation
Perform a constant-time-equivalent workload regardless of whether the user exists: always execute a bcrypt comparison (against a fixed dummy hash) when `FindUser` fails, before returning an error, so that the response time is statistically indistinguishable between existing and nonexistent emails. Apply this fix consistently in `core/sessions/localauth/orm.go` `CreateSession`, and in the equivalent `localLoginFallback` functions in `core/sessions/ldapauth/ldap.go` and `core/sessions/oidcauth/oidc.go`, and in `TestPassword` implementations which have the same short-circuit pattern.

### Proof of Concept
1. Pick a known-valid admin email `valid@example.com` and an email guaranteed not to exist, `nonexistent@example.com`.
2. Send repeated `POST /sessions` requests with an incorrect password for each email:
   - `{"email":"valid@example.com","password":"wrongpass"}`
   - `{"email":"nonexistent@example.com","password":"wrongpass"}`
3. Measure and average response times over many samples (e.g. 100+ requests each, respecting rate limits or spread over time/IPs).
4. Requests for `valid@example.com` will consistently take measurably longer (bcrypt cost factor, typically tens of milliseconds) than `nonexistent@example.com` (DB row-not-found, sub-millisecond), confirming the ability to enumerate valid usernames via `core/sessions/localauth/orm.go:144-162`.

### Citations

**File:** core/web/sessions_controller.go (L34-60)
```go
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
