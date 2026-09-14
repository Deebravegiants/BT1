This chainlink codebase has a directly analogous bug class to the Liferay LDAP import log-exposure CVE: the LDAP authenticator logs user email addresses in plaintext at `Info` level during login flows, and this behavior is present across `ldapauth`, `oidcauth`, and `localauth` session providers, all reachable by an unprivileged client via the `CreateSession` (login) HTTP endpoint.

### Title
Plaintext User Email Addresses Written to Application Log Files During LDAP/OIDC/Local Login - (File: core/sessions/ldapauth/ldap.go)

### Summary
The `ldapauth`, `oidcauth`, and `localauth` session providers log user email addresses at `Info`/`Warn` level on every login attempt (success and failure), writing personally identifiable information (PII) directly into the node's application log files, mirroring CWE-532 "Information Exposure Through Log File" — the same bug class as the referenced Liferay LDAP import advisory.

### Finding Description
`CreateSession` in the LDAP authenticator logs the full email address of the authenticating user on every successful login: `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` [1](#0-0) . The same code path also logs the email on partial failures, e.g. `l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)` [2](#0-1) , and `FindUser` logs emails on lookup failures: `l.lggr.Warnf("No local users table user found with email %s", email)` and `l.lggr.Warnf("User '%s' found but no matching assigned groups in LDAP to assume role", email)` [3](#0-2) .

The OIDC authenticator's local-admin login fallback exhibits the same pattern, logging emails on every local login: `oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)` [4](#0-3) .

The `localauth` ORM similarly attaches the email to the logger context and writes info logs during session creation: `lggr := o.lggr.With("user", user.Email)` followed by `lggr.Debugw("Found user")` and `lggr.Infof("No MFA for user. Creating Session")` [5](#0-4) .

All of these logging calls are reachable from the unauthenticated `/sessions` login endpoint (`CreateSession`), meaning every login attempt — successful or failed, by any client that can reach the API — results in the submitted email address being written verbatim into the node operator's log files, which may be aggregated to centralized log services, log-shipping pipelines, or observability tooling with broader access than the application itself.

### Impact Explanation
This is a low/medium-severity information exposure: node operator log files (and any downstream log aggregation infrastructure) will contain a plaintext record of every login email, including emails submitted in failed attempts (which may not correspond to real accounts, or which an attacker used for enumeration attempts). This matches CVE-2025-62262's classification (CVSS 4.0, "Medium", VC:L) — low confidentiality impact, since email is a relatively low-sensitivity secret. There is no direct authentication/role bypass, no credential leakage, and no fund-movement path; the exposure is limited to email addresses in logs.

### Likelihood Explanation
Every call to the login endpoint (`/sessions`, mapped to `CreateSession`) triggers this logging on the standard success/failure paths, so the exposure occurs with high frequency and requires no special privilege — it happens automatically whenever anyone (including unauthenticated actors submitting failed login attempts) contacts the login endpoint.

### Recommendation
Remove or redact the email address from the `Infof`/`Warnf`/`Debugw` log statements in `core/sessions/ldapauth/ldap.go` (`CreateSession`, `FindUser`), `core/sessions/oidcauth/oidc.go` (`CreateSession`), and `core/sessions/localauth/orm.go` (`CreateSession`), e.g. log a hashed/truncated identifier or omit the email entirely, keeping only role/outcome fields, consistent with the redaction pattern already used for password fields in `core/web/router.go`'s `isBlacklisted`/`redact` helpers [6](#0-5) .

### Proof of Concept
1. Send a login request to the Chainlink node's `/sessions` endpoint with any email/password, whether the credentials are valid or not.
2. Observe the node's application log output (stdout or configured log sink) — the submitted email address appears verbatim in an `INFO` or `WARN` level entry, e.g. `Successful LDAP login request for user alice@example.com - admin` or `No local users table user found with email bob@example.com`.
3. Repeat with different emails to confirm every attempted login email is persisted to the log file, regardless of success.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L179-193)
```go
			l.lggr.Warnf("No local users table user found with email %s", email)
			return sessions.User{}, errors.New("no users found with provided email")
		}

		// If the above query to the local users table was successful, return that local user's role
		return sessions.User{
			Email: email,
			Role:  localUserRole,
		}, nil
	}

	// Populate found user by email and role based on matched group names
	userRole, err := l.groupSearchResultsToUserRole(result.Entries)
	if err != nil {
		l.lggr.Warnf("User '%s' found but no matching assigned groups in LDAP to assume role", email)
```

**File:** core/sessions/ldapauth/ldap.go (L416-419)
```go
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
```

**File:** core/sessions/ldapauth/ldap.go (L435-435)
```go
	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)
```

**File:** core/sessions/oidcauth/oidc.go (L418-420)
```go
	sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
	sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
	oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)
```

**File:** core/sessions/localauth/orm.go (L144-178)
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
```

**File:** core/web/router.go (L643-658)
```go
// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```
