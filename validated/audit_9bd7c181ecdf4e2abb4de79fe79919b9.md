Confirmed: `SessionsController.Create` binds the JSON body unsanitized into `sr.Email` and passes it directly to `AuthenticationProvider().CreateSession` [1](#0-0) . In the LDAP driver, `sr.Email` is logged raw at the success path, and `escapedEmail` (only `ldap.EscapeFilter`-escaped, not newline-escaped) is logged on the group-lookup error path [2](#0-1) [3](#0-2) . The OIDC driver's analogous code explicitly strips `\n`/`\r` before logging, confirming the LDAP path lacks equivalent sanitization [4](#0-3) . `EscapeFilter` only escapes LDAP filter metacharacters and does not neutralize CR/LF or other control characters used for log injection.

This confirms the reported code paths exist exactly as described and there is no sanitization/middleware neutralizing the injection before the log call.

Audit Report

## Title
Unsanitized user-supplied email logged in LDAP login path, enabling log injection (CWE-117) - (File: core/sessions/ldapauth/ldap.go)

## Summary
The `POST /sessions` login endpoint accepts an unauthenticated, client-supplied `email` field and forwards it unsanitized into structured log messages within `ldapAuthenticator.CreateSession`. Unlike the OIDC driver, which explicitly strips `\r`/`\n` before logging the equivalent value, the LDAP driver logs `sr.Email` raw and logs `escapedEmail` (which is only LDAP-filter-escaped, not newline-escaped), allowing a remote unauthenticated actor to inject control characters into log output.

## Finding Description
`SessionsController.Create` binds the JSON request body directly into `clsessions.SessionRequest{Email, Password, ...}` with no sanitization (core/web/sessions_controller.go, L35-39), then passes it to `AuthenticationProvider().CreateSession(ctx, sr)` (L56). When the LDAP driver is configured, `ldapAuthenticator.CreateSession` computes `escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))`, which only escapes LDAP filter metacharacters (`*`, `(`, `)`, `\`, NUL) — it does not strip or escape `\r`/`\n`. This value is logged on the group-lookup error path: `l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)`. On the success path, the raw, fully unsanitized `sr.Email` is logged directly: `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)`. The equivalent OIDC driver code (`oidcauth/oidc.go`, L418-420) explicitly strips `\n` and `\r` before the analogous log call, demonstrating the project recognizes this risk class but failed to apply the same mitigation in the LDAP path. No sanitization or output-neutralization occurs anywhere in the request path (`SessionsController.Create` → `CreateSession`) before these log calls.

## Impact Explanation
An attacker who can reach `POST /sessions` (unauthenticated by design, as it is the login endpoint) can submit an `email` value containing embedded `\r`/`\n` sequences. In text/console-formatted log output, this can forge fabricated log lines that impersonate a different actor's successful login, corrupt log parsing in downstream SIEM/log-ingestion pipelines that rely on line boundaries, and potentially inject terminal control sequences if logs are viewed raw. This maps to CWE-117 (Improper Output Neutralization for Logs) and falls under audit-log integrity / cross-user log/response corruption concerns.

## Likelihood Explanation
High reachability: `/sessions` is unauthenticated, `email` is fully attacker-controlled, and no sanitization occurs before the vulnerable log statements. The only gating condition is that the LDAP authentication driver must be enabled/configured (a supported, non-default but standard deployment configuration, not an operator-only or misconfiguration precondition — it is a normal enterprise auth mode). Any request reaching the LDAP `CreateSession` path — including bind failures with local-fallback failures, or successful logins — can trigger one of the two vulnerable log statements.

## Recommendation
Sanitize all user-supplied fields before writing them to logs in `core/sessions/ldapauth/ldap.go`, consistent with the mitigation already present in `core/sessions/oidcauth/oidc.go` — i.e., strip `\r`/`\n` (or apply a shared log-sanitization helper) before logging `sr.Email` and `escapedEmail` in `ldapAuthenticator.CreateSession`, and audit `FindUser`/`FindUserByAPIToken` for the same pattern.

## Proof of Concept
1. Configure chainlink with the LDAP authentication driver enabled.
2. Send: `POST /sessions` with body `{"email":"attacker@example.com\nlevel=info msg=\"Successful LDAP login request for user admin@example.com - admin\"","password":"anything"}`.
3. If LDAP bind fails and the `FindUser` group lookup also fails, the log line `l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)` at `core/sessions/ldapauth/ldap.go:418` is emitted with the embedded newline; alternatively, if authentication with the LDAP server succeeds, `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` at line 435 emits the raw string, splitting into two apparent log lines in text-formatted output — one forged to look like a legitimate login by `admin@example.com`. A Go unit test invoking `ldapAuthenticator.CreateSession` with a crafted `sr.Email` containing `\n`/`\r` against a captured `zap`/`sugared` logger output (or a test logger core) can assert that the resulting log record contains unescaped newline-separated content.

### Citations

**File:** core/web/sessions_controller.go (L35-56)
```go
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
