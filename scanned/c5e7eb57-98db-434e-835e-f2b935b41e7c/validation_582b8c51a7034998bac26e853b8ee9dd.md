### Title
Username enumeration via authentication timing side-channel in session login (`POST /sessions`) - ([File: core/sessions/localauth/orm.go])

### Summary
The `CreateSession` login flow performs an unauthenticated user lookup and returns immediately on a "user not found" error, before any expensive password-hash comparison ever runs. Only when the email exists does the code proceed to `utils.CheckPasswordHash`, which invokes bcrypt (deliberately slow, ~tens of ms). This produces the same class of bug reported in the Traefik advisory (CVE-2026-41263): a response-time oracle that distinguishes "user exists" (slow bcrypt path) from "user does not exist" (fast DB-miss path), allowing unauthenticated username/email enumeration.

### Finding Description
`SessionsController.Create` (`core/web/sessions_controller.go:29-68`) is an unauthenticated, internet-facing endpoint (`POST /sessions`) that accepts an email/password pair and calls `AuthenticationProvider().CreateSession`.

In the local auth backend, `CreateSession` first resolves the user by email and short-circuits on failure, well before any constant-cost cryptographic work: [1](#0-0) 

```
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	...
	if !constantTimeEmailCompare(...) { ... }
	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) { ... }
```

`FindUser` is a simple, fast SQL lookup: [2](#0-1) 

For a non-existent email, the function returns after only a DB miss (microseconds to low milliseconds). For an existing email with a wrong password, execution reaches `utils.CheckPasswordHash`, which wraps `bcrypt.CompareHashAndPassword` — an intentionally expensive, cost-factor-driven operation: [3](#0-2) 

The `constantTimeEmailCompare` helper only protects against timing differences *between* two known email strings byte-by-byte; it does nothing to equalize the cost between the "row not found" fast path and the "row found, bcrypt executed" slow path: [4](#0-3) 

The identical pattern (DB lookup fails fast, DB lookup succeeds then runs bcrypt) also exists in the LDAP and OIDC local-fallback login paths: [5](#0-4) [6](#0-5) 

This is the exact bug class described in the Traefik advisory: a comparison that is supposed to run at constant cost regardless of whether the credential subject exists, but instead fast-fails for non-existent identities and only performs the expensive (bcrypt) comparison for existing ones — restoring a timing oracle for identity enumeration.

### Impact Explanation
An unauthenticated network attacker can send crafted email/password pairs to `POST /sessions` and measure response latency to determine whether a given email address corresponds to a real Chainlink node operator/API user account, without needing any credentials. This is username/account enumeration (CWE-208), matching the "cross-user response confusion" / authentication-oracle impact class. It does not by itself grant access, but it materially aids credential-stuffing and targeted brute-force/social-engineering attacks against the node's operator UI and API, since Chainlink node UI/API login has no other rate-limiting or lockout evident in this flow.

### Likelihood Explanation
The `/sessions` endpoint is reachable pre-authentication by any client able to reach the node's web/API port, so likelihood of exploitation attempts is high wherever the node UI/API is exposed. However, exploitation requires many timing samples (statistical technique, as in the Traefik PoC) to overcome network jitter, so it is a Medium-severity, high-effort-but-feasible timing attack rather than a trivial one — consistent with the CVSS AC:H rating in the source advisory.

### Recommendation
Ensure the login path performs the same fixed, expensive comparison work whether or not the requested email exists — e.g., always execute a dummy `bcrypt.CompareHashAndPassword` call against a fixed/precomputed hash when the user lookup fails (mirroring the fix pattern in the referenced advisory), instead of returning immediately from `FindUser` errors before any hashing occurs. Apply the same fix to the `localLoginFallback` paths in `ldapauth` and `oidcauth`.

### Proof of Concept
1. Deploy a Chainlink node with local auth enabled and at least one API user created.
2. Send repeated `POST /sessions` requests with `{"email": "<existing-email>", "password": "wrong"}` and measure round-trip time; expect ~tens of ms (bcrypt cost) dominating latency.
3. Send repeated `POST /sessions` requests with `{"email": "<random-nonexistent-email>", "password": "wrong"}` and measure round-trip time; expect sub-millisecond-to-few-millisecond latency (simple DB miss, no bcrypt).
4. Compare the two latency distributions (as in the Traefik PoC's median-ratio classification) to reliably distinguish existing vs. non-existing accounts, confirming the timing oracle in `core/sessions/localauth/orm.go:144-162`.

### Citations

**File:** core/sessions/localauth/orm.go (L44-59)
```go
func (o *orm) FindUser(ctx context.Context, email string) (sessions.User, error) {
	return o.findUser(ctx, email)
}

// FindUserByAPIToken will attempt to return an API user via the user's table token_key column.
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1"
	err = o.ds.GetContext(ctx, &user, sql, apiToken)
	return
}

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

**File:** core/sessions/localauth/orm.go (L232-241)
```go
const constantTimeEmailLength = 256

func constantTimeEmailCompare(left, right string) bool {
	length := mathutil.Max(constantTimeEmailLength, len(left), len(right))
	leftBytes := make([]byte, length)
	rightBytes := make([]byte, length)
	copy(leftBytes, left)
	copy(rightBytes, right)
	return subtle.ConstantTimeCompare(leftBytes, rightBytes) == 1
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

**File:** core/sessions/ldapauth/ldap.go (L624-642)
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
}
```

**File:** core/sessions/oidcauth/oidc.go (L580-597)
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
}
```
