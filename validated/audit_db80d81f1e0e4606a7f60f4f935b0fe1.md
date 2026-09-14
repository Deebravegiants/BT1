### Title
Timing-Based Account Enumeration in Login Flow via Early-Return `FindUser` Before Password Hashing - ([File: core/sessions/localauth/orm.go])

### Summary
The local authentication login flow (`CreateSession`) queries for a user by email and returns immediately with an error if no matching row exists, only performing the expensive `bcrypt` password comparison when an account is actually found. This produces a measurable timing difference between "email exists" and "email does not exist" responses, mirroring the exact bug class described in GHSA-r6mm-wmhf-849m (TYPO3 Flow `PersistedUsernamePasswordProvider`), where hashing was skipped when no account was found.

### Finding Description
In `core/sessions/localauth/orm.go`, `CreateSession` calls `o.FindUser(ctx, sr.Email)` first and returns early on error, before any password comparison happens: [1](#0-0) 

The same early-return-before-hash pattern also appears in the LDAP and OIDC local-fallback and `TestPassword` implementations, which query the DB for `hashed_password` and immediately return an "invalid credentials" style error if the row is not found, skipping `utils.CheckPasswordHash` (bcrypt) entirely for non-existent accounts: [2](#0-1) [3](#0-2) [4](#0-3) 

`utils.CheckPasswordHash` wraps `bcrypt.CompareHashAndPassword`, which is deliberately slow (tunable cost factor), so its absence for non-existent emails creates an observable timing gap versus the case where an account exists (DB lookup + bcrypt compare): [5](#0-4) 

This is reachable unauthenticated via the login endpoint (`POST /sessions`, wired through `router.go`), which is the exact analog required: an unprivileged actor submitting login credentials can distinguish valid vs. invalid emails purely from response timing, without needing valid credentials.

Note: constant-time comparison is applied to the *email string* itself (`constantTimeEmailCompare`) once a user row is found, and to token secrets via `subtle.ConstantTimeCompare` elsewhere — but this only protects a compare between the *found* row's email and the submitted email; it does nothing to close the timing gap between "row found → do bcrypt" and "row not found → skip bcrypt" for the initial existence check. [6](#0-5) 

### Impact Explanation
An external, unauthenticated attacker can use this timing side-channel to enumerate valid email addresses/usernames registered on a chainlink node's Operator UI, without needing to guess passwords. This is account-existence information disclosure — a building block for targeted credential stuffing, phishing, or brute-force attacks against confirmed accounts. It does not by itself grant authentication or role bypass, key disclosure, or fund movement.

### Likelihood Explanation
Exploitability requires network timing measurement over the `/sessions` endpoint, which can be noisy in production but is a well-established, practical technique (many repeated requests can average out network jitter). The rate limiting seen in `TestSessions_RateLimited` may partially mitigate brute-scale enumeration, but the underlying logic bug is unconditional and present regardless of the rate limiter: [7](#0-6) 

### Recommendation
Perform a constant-time-equivalent password hash comparison regardless of whether the email was found, e.g. always run `utils.CheckPasswordHash` against either the real stored hash or a precomputed dummy/static bcrypt hash when no user is found, before branching on existence. Apply this uniformly in `orm.CreateSession`/`TestPassword` (`core/sessions/localauth/orm.go`), `ldapAuthenticator.localLoginFallback`/`TestPassword` (`core/sessions/ldapauth/ldap.go`), and `oidcAuthenticator.localLoginFallback`/`TestPassword` (`core/sessions/oidcauth/oidc.go`).

### Proof of Concept
1. Send `POST /sessions` with `{"email":"nonexistent@test.com","password":"x"}` repeatedly and measure response latency (fails fast: DB miss only).
2. Send `POST /sessions` with `{"email":"<known-existing-admin-email>","password":"wrongpassword"}` repeatedly and measure latency (slower: DB hit + bcrypt compare).
3. Compare the two latency distributions — the bcrypt-compare path is consistently and measurably slower, allowing an attacker to distinguish "email exists" from "email doesn't exist" purely from timing, as demonstrated by the code paths cited above in `CreateSession`.

### Citations

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

**File:** core/sessions/localauth/orm.go (L309-318)
```go
func (o *orm) TestPassword(ctx context.Context, email string, password string) error {
	var hashedPassword string
	if err := o.ds.GetContext(ctx, &hashedPassword, "SELECT hashed_password FROM users WHERE lower(email) = lower($1)", email); err != nil {
		return pkgerrors.New("no matching user for provided email")
	}
	if !utils.CheckPasswordHash(password, hashedPassword) {
		return pkgerrors.New("passwords don't match")
	}
	return nil
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

**File:** core/sessions/ldapauth/ldap.go (L814-823)
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

**File:** core/sessions/oidcauth/oidc.go (L488-498)
```go
func (oi *oidcAuthenticator) TestPassword(ctx context.Context, email string, password string) error {
	// Fall back to test local users table in case of supported local CLI users as well
	var hashedPassword string
	if err := oi.ds.GetContext(ctx, &hashedPassword, "SELECT hashed_password FROM users WHERE lower(email) = lower($1)", email); err != nil {
		return errors.New("invalid credentials")
	}
	if !utils.CheckPasswordHash(password, hashedPassword) {
		return errors.New("invalid credentials")
	}
	return nil
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

**File:** core/web/router_test.go (L127-148)
```go
func TestSessions_RateLimited(t *testing.T) {
	t.Parallel()

	ctx := t.Context()
	app := cltest.NewApplicationEVMDisabled(t)
	require.NoError(t, app.Start(ctx))

	router := web.Router(t, app, nil)
	ts := httptest.NewServer(router)
	defer ts.Close()

	client := clhttptest.NewTestLocalOnlyHTTPClient()
	input := `{"email":"brute@force.com", "password": "wrongpassword"}`

	for range 5 {
		request, err := http.NewRequestWithContext(ctx, http.MethodPost, ts.URL+"/sessions", bytes.NewBufferString(input))
		require.NoError(t, err)

		resp, err := client.Do(request)
		require.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
	}
```
