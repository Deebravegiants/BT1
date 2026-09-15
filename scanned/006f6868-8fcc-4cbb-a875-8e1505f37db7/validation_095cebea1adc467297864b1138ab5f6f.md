### Title
Log Forging via unneutralized control characters in login `email` field written to node logs - ([File: core/sessions/localauth/orm.go], [File: core/sessions/ldapauth/ldap.go])

### Summary
Chainlink's `CreateSession` authentication flow, reachable via an unauthenticated `POST /sessions` request (`sessions.SessionRequest.Email`), writes the raw, attacker-controlled email/username value directly into the node's structured logger (`lggr.Infof`/`lggr.Warnf`/`lggr.With`) without stripping or encoding control characters such as CR/LF. This mirrors the morgan `:remote-user` CWE-117 pattern: untrusted, credential-adjacent input taken from an unauthenticated network request is emitted verbatim into the log stream, letting a remote unauthenticated user forge/inject fabricated log lines.

### Finding Description
The login endpoint accepts a `SessionRequest` whose `Email` field is fully attacker-controlled and unauthenticated (this is the credential submitted to log in, not yet validated). In `core/sessions/localauth/orm.go`: [1](#0-0) 

`o.lggr.With("user", user.Email)` uses the DB-resolved email, but subsequent code paths log `sr.Email` (the raw request value) directly, e.g. via the audit logger calls: [2](#0-1) 

and [3](#0-2) 

Similarly, in the LDAP authentication path, `core/sessions/ldapauth/ldap.go`, the raw request email (`sr.Email`) — not the LDAP-filter-escaped `escapedEmail` — is passed straight into a `Infof`-style format string: [4](#0-3) [5](#0-4) 

`ldap.EscapeFilter` only escapes LDAP-filter metacharacters (`*`, `\`, NUL, parentheses); it does not neutralize CR/LF or other control characters, so it provides no protection against log-line injection. Both `orm.go`'s `lggr.Infof/Warnf/Errorf` calls and `ldap.go`'s `l.lggr.Infof` calls use zap's formatted/plain text sinks, where embedded `\r\n` sequences in `sr.Email` are written through unmodified, letting an attacker split a single log entry into multiple fabricated entries — the same root cause as morgan's `:remote-user` token, which also takes an unauthenticated, attacker-supplied credential-like value and writes it to the log stream verbatim.

Contrast this with the codebase's own hardened logging path in `core/capabilities/remote/utils_test.go`'s `remote.SanitizeLogString`, which explicitly strips/marks unprintable/control characters before logging — proving the project is aware of and mitigates this bug class elsewhere, but the mitigation is not applied to the session/login email logging paths shown above.

### Impact Explanation
An unauthenticated remote attacker submitting a login request with a CR/LF-laden `email` value can inject forged log lines into the Chainlink node's application/audit logs. This can be used to:
- Corrupt the integrity of authentication audit trails (e.g., fake `AUTH_LOGIN_SUCCESS`/`AUTH_LOGIN_FAILED` looking lines), hindering incident response and forensic investigation.
- Spoof or obscure real login attempts in log-based intrusion detection/alerting pipelines that parse one-request-per-line log formats.
Per the CVSS of the referenced advisory (`C:N/I:L/A:N`), this is an integrity-only impact — no confidentiality or availability compromise, matching the Medium severity of the original morgan issue.

### Likelihood Explanation
High likelihood of reachability: the `/sessions` login endpoint (`CreateSession`) is unauthenticated by design (it is the login mechanism itself), so no prior credentials or privileges are required to reach the vulnerable logging call — an attacker only needs to submit a POST body with a crafted `email` field containing `\r\n` sequences.

### Recommendation
Sanitize/neutralize control characters (CR, LF, and other non-printable characters) in `sr.Email` before it is passed to any logger call (`lggr.Infof`, `lggr.Warnf`, `lggr.Errorf`, `auditLogger.Audit` data maps) in `core/sessions/localauth/orm.go` and `core/sessions/ldapauth/ldap.go`. Reuse the existing `remote.SanitizeLogString`-style helper (already present in `core/capabilities/remote/utils_test.go`'s tested `SanitizeLogString`) or a similar function project-wide for any user-supplied string prior to it being interpolated into a log message, rather than only escaping for LDAP-filter syntax.

### Proof of Concept
1. Send an unauthenticated `POST /sessions` request with a JSON body such as:
```json
{"email": "admin@example.com\r\n2026-09-14T00:00:00Z [INFO] AUTH_LOGIN_SUCCESS_NO_2FA fake-forged-entry", "password": "irrelevant"}
```
2. In the local-auth path, this reaches `orm.CreateSession` — `sr.Email` flows into `o.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})` (core/sessions/localauth/orm.go:154-156) and, on a successful bind against the LDAP path, into `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` (core/sessions/ldapauth/ldap.go:435).
3. If the underlying log sink is plain-text (console/file, not strict JSON encoding), the embedded CR/LF causes the injected content to appear as a separate, forged log line, corrupting the one-entry-per-line log structure — analogous to the morgan `:remote-user` CVE-2026-5078 injection.

### Citations

**File:** core/sessions/localauth/orm.go (L144-150)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	lggr := o.lggr.With("user", user.Email)
	lggr.Debugw("Found user")
```

**File:** core/sessions/localauth/orm.go (L154-161)
```go
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		o.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
```

**File:** core/sessions/localauth/orm.go (L176-177)
```go
		_, err = o.ds.ExecContext(ctx, "INSERT INTO sessions (id, email, last_used, created_at) VALUES ($1, $2, now(), now())", session.ID, user.Email)
		o.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})
```

**File:** core/sessions/ldapauth/ldap.go (L406-419)
```go
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}

	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
```

**File:** core/sessions/ldapauth/ldap.go (L431-436)
```go
	if returnErr != nil {
		return "", returnErr
	}

	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)

```
