### Title
Unauthenticated login email is interpolated unsanitized into server log messages, enabling log-entry forgery/splitting via newline injection - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The LDAP session-creation path logs the caller-supplied `sr.Email` field directly into formatted log messages using `%v`/`%s`-style logging (`Infof`), without stripping control characters such as `\n` or `\r`. Because `CreateSession` is reachable by any unauthenticated client submitting login credentials, an attacker can embed newlines in the email field to inject arbitrary-looking extra log lines or split a legitimate line — the same bug class as CVE-2021-20333 (MongoDB "artificial log entries ... or log entries to be split").

### Finding Description
`ldapAuthenticator.CreateSession` accepts a `sessions.SessionRequest` from an unprivileged/unauthenticated caller (the login endpoint) and logs the caller-controlled email value verbatim in several places using printf-style formatting rather than structured key-value logging that would be safely escaped: [1](#0-0) [2](#0-1) 

Specifically:
- `l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)` — not attacker data, but adjacent code shows the pattern.
- `l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)`
- `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)`

`sr.Email` originates straight from the HTTP request body via `SessionsController.Create`, which binds JSON into `clsessions.SessionRequest` and forwards it unmodified to `CreateSession`: [3](#0-2) 

Unlike the codebase's structured `Infow`/`Errorw`/`Debugw` calls elsewhere (which pass values as typed zap fields), these calls build the log message string via `fmt`-style formatting before it reaches the logger. Depending on the configured zap encoder (console vs JSON), an embedded `\n`/`\r` in the email value can be written to the underlying log stream as a literal line break, effectively fabricating additional log lines or splitting the original line — mirroring the MongoDB CVE's "artificial log entries" / "log entries ... split" behavior. I was not able to conclusively confirm from the available code whether the default node logger encoder is the zap console encoder (which does not escape embedded control characters in the message) or the JSON encoder (which would escape `\n` as `\n` text and prevent the injection); `makeEncoderConfig` only configures shared fields (time/level encoders) and the encoder type selection lives in `core/logger/logger.go`, which I could not fully inspect within the available tool budget.

### Impact Explanation
If the deployed encoder does not escape control characters (e.g., console encoding, which many self-hosted/on-prem Chainlink node operators use for readability), an attacker who merely attempts to log in — no valid credentials required — can inject fabricated log lines (e.g., fake "successful login" or fake error entries) or truncate/split genuine audit-relevant log lines. This can be used to mislead operators/SIEM tooling monitoring node logs, hide malicious activity, or frame another user, degrading the integrity of the audit trail used for security monitoring of node authentication events.

### Likelihood Explanation
Likelihood is bounded by (a) requiring `CreateSession`/LDAP auth to actually be configured and reachable (LDAP is an optional auth backend), and (b) depending on the actual log encoder in use, which was not confirmed. Where applicable, the attack requires no authentication and no special privileges — any request to the login endpoint with a crafted `email` field is sufficient to reach the vulnerable log statement.

### Recommendation
- Replace the `Infof`/format-string logging of user-controlled fields with structured logging (`Infow("...", "email", sr.Email, ...)`), consistent with the rest of the codebase, so the logger's encoder is responsible for safely escaping the value.
- As defense-in-depth, sanitize/strip control characters (`\n`, `\r`, other C0 controls) from user-supplied identifiers (email) before any logging, regardless of encoder.
- Audit remaining `Infof`/`Errorf`/`Debugf`-style calls across `core/` for other instances where unauthenticated-request-derived strings (emails, request IDs, headers) are interpolated into log messages rather than passed as structured fields.

### Proof of Concept
1. Configure the node with LDAP authentication enabled.
2. POST to the session creation endpoint (`/sessions`) with a JSON body such as:
```json
{"email": "attacker@example.com\n2026-09-13T00:00:00Z\tINFO\tSuccessful LDAP login request for user admin@example.com - Role: admin", "password": "wrong"}
```
3. If the LDAP bind fails and local fallback also fails, the flow still reaches `FindUser`/error logging paths that echo the raw email; if bind succeeds (or the analogous unauthenticated echo point is hit) the line:
```go
l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)
```
is invoked with the crafted `sr.Email`, producing an extra forged log line if the configured encoder does not escape embedded newlines.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L405-420)
```go
	// Attempt to LDAP Bind with user provided credentials
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
	}
```

**File:** core/sessions/ldapauth/ldap.go (L435-436)
```go
	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)

```

**File:** core/web/sessions_controller.go (L34-56)
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
```
