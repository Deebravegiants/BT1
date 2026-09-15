## Analysis

The CKAN advisory describes an unauthenticated user-controlled parameter being written directly into the application log via string formatting, without filtering for newlines — enabling log forgery/injection (CWE-117/CWE-532).

Chainlink's LDAP login authenticator has the same pattern.

### Title
Log injection via unsanitized user email in LDAP login flow - (File: core/sessions/ldapauth/ldap.go)

### Summary
The `ldapAuthenticator.CreateSession` function logs the raw, attacker-supplied `sr.Email` value using `Infof` string-formatting (not structured key-value logging) without stripping `\n`/`\r` characters, unlike the equivalent OIDC code path which explicitly sanitizes the same field before logging.

### Finding Description
`SessionsController.Create` is the handler for the public, unauthenticated login endpoint (`POST /sessions`). It binds the request JSON body into a `clsessions.SessionRequest` and forwards it unmodified to the configured `AuthenticationProvider().CreateSession` implementation. [1](#0-0) 

When the LDAP authentication driver is configured, this reaches `ldapAuthenticator.CreateSession`, which logs the caller-controlled `sr.Email` directly with `%s` formatting into an info-level log message on a successful login:
```go
l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)
``` [2](#0-1) 

The intermediate `escapedEmail` value used earlier in the same function is passed only through `ldap.EscapeFilter`, which escapes LDAP filter metacharacters (`(`, `)`, `\`, `*`, NUL) — it does not strip or escape `\n`/`\r`, so it also flows unsanitized into the log at line 418: [3](#0-2) 

By contrast, the OIDC authenticator's equivalent local-admin login path explicitly strips `\n` and `\r` from the same `sr.Email` field before logging it, showing this exact bug class was already identified and remediated for one authenticator but not for LDAP: [4](#0-3) 

Since `sr.Email` comes straight from the JSON body of an unauthenticated `POST /sessions` request, an attacker can embed `\n`/`\r` sequences (and additional forged-looking log tokens) in the email field to inject fabricated log lines or corrupt the log format — the same root cause as CVE-2024-27097.

### Impact Explanation
An unauthenticated attacker can forge or corrupt application log entries by injecting newline-delimited fake log lines through the `email` field of the login request. This can be used to fabricate misleading audit/log evidence (e.g., fake "successful login" entries for other users), pollute log-based monitoring/alerting, or break downstream log parsers that assume one log record per line. Impact is limited to log integrity/confidentiality of log stream formatting, not direct authentication bypass or fund movement, consistent with the CVSS `C:N/I:L/A:N` rating of the original advisory.

### Likelihood Explanation
High likelihood of reachability: the `/sessions` endpoint is intentionally unauthenticated (it's the login endpoint), takes freeform `email`/`password` JSON fields, and the vulnerable log statement is on the success path of `CreateSession`, executed whenever LDAP bind and user lookup succeed. No privileges are required to trigger it — only a valid (or attacker-controlled) LDAP-bindable account, or reaching the fallback local-admin flow.

### Recommendation
Sanitize `sr.Email` (and the LDAP-filter-escaped variant) before logging, mirroring the `oidcauth` fix: strip or escape `\n`/`\r` (and consider control characters generally) prior to any `Infof`/`Errorf`-style formatted logging, or switch to structured logging (`Infow("...", "email", sr.Email)`) so the logger's encoder handles safe serialization rather than raw string interpolation.

### Proof of Concept
1. Configure the node with LDAP authentication enabled and a matching directory user.
2. Send `POST /sessions` with a JSON body such as:
```json
{"email": "victim@example.com\n{\"level\":\"info\",\"msg\":\"Successful LDAP login request for user attacker@evil.com - admin\"}", "password": "validpass"}
```
3. If the bind/user lookup for the crafted (LDAP-escaped) value succeeds (or the attacker controls an account whose email contains an encoded newline sequence accepted by the bind), the resulting log line at `ldap.go:435` will contain an embedded newline, producing a second, attacker-fabricated log record in the node's log stream.

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
