### Title
LDAP unauthenticated-bind may allow empty-password authentication bypass in `TestPassword` - (File: `core/sessions/ldapauth/ldap.go`)

### Summary
`ldapAuthenticator.TestPassword` forwards a user-supplied password directly to `conn.Bind(searchBaseDN, password)` without first verifying that the password is non-empty. Per the LDAP protocol (RFC 4513 §5.1.2), a Bind request with a valid DN and an *empty* password is defined as an "unauthenticated bind" and many LDAP servers will return success (`err == nil`) for it without actually validating any credential. The Go code treats any non-error return from `Bind` as proof of successful authentication, exactly mirroring the root cause in the external report: a downstream call's non-standard success/failure semantics are not accounted for by the caller, so a case that is not truly "authenticated" is mistakenly treated as authenticated.

### Finding Description [1](#0-0) 

```go
func (l *ldapAuthenticator) TestPassword(ctx context.Context, email string, password string) error {
	conn, err := l.ldapClient.CreateEphemeralConnection()
	...
	err = conn.Bind(searchBaseDN, password)
	if err == nil {
		return nil
	}
	...
}
```

There is no check that rejects an empty `password` before it is passed to `conn.Bind`. The LDAP protocol's `Bind` operation has non-standard success semantics in the case of an empty password: it does not fail with an authentication error the way a normal wrong-password bind does — it succeeds as an "unauthenticated bind," signalling only that the DN exists, not that any secret was verified. `err == nil` is used by the code as the sole signal of "the user proved their identity," which is precisely the same class of bug as the report's underlying issue: relying on a raw/underlying call's return value without accounting for a documented deviation from expected (boolean-success) semantics.

This function (`TestPassword`) is reachable from the unprivileged web API — e.g. it backs password confirmation flows such as `DeleteAPIToken` in `core/web/resolver/mutation.go`, which calls `r.App.AuthenticationProvider().TestPassword(ctx, dbUser.Email, args.Input.Password)` to re-verify a user's password before performing an authenticated action. [2](#0-1) 

### Impact Explanation
If the configured upstream LDAP server permits unauthenticated binds for the relevant DN (a common default/legacy configuration, and one not controlled by this codebase), an attacker who already knows or can guess a valid email/DN (which is typically not secret) could submit an empty password and have `TestPassword` return success. Any code path that relies on `TestPassword` as a re-authentication/step-up check (such as confirming password before deleting or rotating an API token) could then be bypassed, allowing an authenticated-but-lower-trust actor (or a session-riding attacker) to perform a sensitive action without actually knowing the victim's password.

### Likelihood Explanation
Likelihood depends entirely on the LDAP server's configuration (whether unauthenticated binds are disabled, which is best practice but not universal, especially for legacy/misconfigured directories). Because the current code does no defensive empty-password check on the chainlink side, the exposure is directly proportional to upstream server posture rather than to any additional application-layer mitigation.

### Recommendation
Explicitly reject empty (or whitespace-only) passwords in `TestPassword` (and any other function invoking `conn.Bind` with a user-supplied password, such as the LDAP session-creation path) before calling `Bind`, e.g.:
```go
if strings.TrimSpace(password) == "" {
    return errors.New("invalid credentials")
}
```
This ensures the code does not depend on the LDAP server correctly rejecting unauthenticated binds, closing the gap between the raw protocol call's actual semantics and the application's interpretation of it — the same fix category recommended in the report (don't trust ambiguous/non-standard success signals from an underlying call; validate explicitly at the call site).

### Proof of Concept
1. Configure (or target) an upstream LDAP server that allows unauthenticated binds (default behavior for many directory servers unless explicitly disabled).
2. As an unprivileged actor with a valid target user's email/DN, invoke a code path that calls `AuthenticationProvider().TestPassword(ctx, email, "")` (e.g., the `DeleteAPIToken` GraphQL mutation with `Input.Password: ""`).
3. `conn.Bind(searchBaseDN, "")` returns `nil` error (unauthenticated bind succeeds), `TestPassword` returns `nil`, and the sensitive action (e.g., deleting the victim's API token) proceeds without real password verification.

Note: I was unable to fully verify, within the tool-call budget, the equivalent `Bind` call sites in `CreateSession`/`SetPassword` in the same file (grep indicated 3 `Bind(` occurrences in `ldap.go`, only one of which — in `TestPassword` — was read in full). Those additional call sites should be reviewed for the same missing empty-password check.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L503-530)
```go
// TestPassword tests if an LDAP login bind can be performed with provided credentials, returns nil if success
func (l *ldapAuthenticator) TestPassword(ctx context.Context, email string, password string) error {
	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		return errors.New("unable to establish connection to LDAP server with provided URL and credentials")
	}
	defer conn.Close()

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
	if err == nil {
		return nil
	}
	l.lggr.Infof("Error binding user authentication request in TestPassword call LDAP Bind: %v", err)

	// Fall back to test local users table in case of supported local CLI users as well
	var hashedPassword string
	if err := l.ds.GetContext(ctx, &hashedPassword, "SELECT hashed_password FROM users WHERE lower(email) = lower($1)", email); err != nil {
		return errors.New("invalid credentials")
	}
	if !utils.CheckPasswordHash(password, hashedPassword) {
		return errors.New("invalid credentials")
	}

	return nil
}
```

**File:** core/web/resolver/mutation.go (L1035-1047)
```go
	dbUser, err := r.App.AuthenticationProvider().FindUser(ctx, session.User.Email)
	if err != nil {
		return nil, err
	}

	err = r.App.AuthenticationProvider().TestPassword(ctx, dbUser.Email, args.Input.Password)
	if err != nil {
		r.App.GetAuditLogger().Audit(audit.APITokenDeleteAttemptPasswordMismatch, map[string]any{"user": dbUser.Email})

		return NewDeleteAPITokenPayload(nil, map[string]string{
			"password": "incorrect password",
		}), nil
	}
```
