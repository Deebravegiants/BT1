### Title
Unsanitized user-supplied email logged in LDAP login path, enabling log injection (CWE-117) - (File: core/sessions/ldapauth/ldap.go)

### Summary
The `POST /sessions` login endpoint accepts an unauthenticated client-supplied `email` field and forwards it, unsanitized, into structured log messages in the LDAP authentication driver's `CreateSession` function. This mirrors the Apache Struts advisory's bug class (CWE-117, Improper Output Neutralization for Logs): untrusted input is written to logs without filtering, allowing a remote unauthenticated actor to inject control characters (e.g. `\r`, `\n`) or crafted text that can forge or confuse log lines.

### Finding Description
`SessionsController.Create` binds the JSON request body directly into `clsessions.SessionRequest{Email, Password, ...}` with no sanitization [1](#0-0) , then passes it to `AuthenticationProvider().CreateSession(ctx, sr)` [2](#0-1) .

For the LDAP driver, `ldapAuthenticator.CreateSession` logs the raw, attacker-controlled `sr.Email` value multiple times without stripping newlines or other control characters:
- On error looking up user groups: `l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)` [3](#0-2) 
- On successful login: `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` [4](#0-3) 

Notably, the equivalent OIDC driver code explicitly strips `\n` and `\r` from the email before logging in its analogous `CreateSession` login-success log line, showing the project is aware of this exact risk class but did not apply the same mitigation in the LDAP path: [5](#0-4) 

The LDAP bind failure path also logs unsanitized input indirectly via `escapedEmail`, which is only LDAP-filter-escaped (`ldap.EscapeFilter`), not newline/log-escaped: [6](#0-5) 

### Impact Explanation
An unauthenticated attacker who can reach the `/sessions` endpoint can submit an `email` value containing embedded newlines or other formatting characters. Depending on the log encoder/output sink in use, this can allow the attacker to inject fabricated log lines (masquerading as separate, unrelated log entries) or corrupt structured-log parsing/ingestion pipelines that key off line boundaries — precisely the impact described in CWE-117/CVE-2025-54656. This can be used to plant misleading audit trails (e.g., forging a fake "successful login" entry for a different user), confuse SOC/SIEM tooling, or facilitate downstream log-injection-based attacks (e.g., terminal escape sequence injection if logs are viewed in a raw terminal).

### Likelihood Explanation
High reachability: the `/sessions` `POST` endpoint is unauthenticated by design (it's the login endpoint) and the `email` field is fully attacker-controlled from the request body, with no application-layer sanitization before it reaches the log call. The only gating factor is that this specific vulnerable branch is exercised only when the LDAP authentication provider is configured/enabled.

### Recommendation
Sanitize (or structurally encode) all user-supplied fields before writing them to logs in `core/sessions/ldapauth/ldap.go`, consistent with the mitigation already applied in `core/sessions/oidcauth/oidc.go` (stripping `\r`/`\n`, or better, using a dedicated log-sanitization helper applied consistently across all authenticators). Apply this to every log statement in `ldapAuthenticator.CreateSession` (and `FindUser`/`FindUserByAPIToken`) that logs `sr.Email`, `escapedEmail`, or any other externally supplied value.

### Proof of Concept
1. Configure chainlink with the LDAP authentication driver enabled.
2. Send an unauthenticated request:
```
POST /sessions
Content-Type: application/json

{"email":"attacker@example.com\nlevel=info msg=\"Successful LDAP login request for user admin@example.com - admin\"","password":"anything"}
```
3. If LDAP bind fails and the local fallback path also fails, the branch at `l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)` is reached with the injected value, or, if authentication otherwise proceeds to completion, `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` writes the raw string, splitting into what appears to be two separate structured log lines in text/console-formatted log output — one attacker-controlled forged entry impersonating a different user's successful login.

### Citations

**File:** core/web/sessions_controller.go (L35-39)
```go
	var sr clsessions.SessionRequest
	if err := c.ShouldBindJSON(&sr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("error binding json %w", err))
		return
	}
```

**File:** core/web/sessions_controller.go (L56-56)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
```

**File:** core/sessions/ldapauth/ldap.go (L406-410)
```go
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
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
