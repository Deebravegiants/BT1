### Title
LDAP Bind DN Injection via Insufficiently Escaped User-Supplied Email in Authentication Flow - (File: core/sessions/ldapauth/ldap.go)

### Summary
The LDAP authentication provider's `CreateSession` and `TestPassword` functions build the LDAP bind Distinguished Name (DN) by inserting a user-controlled email address that has only been sanitized with `ldap.EscapeFilter`, a function intended for escaping LDAP **search filter** metacharacters (`*`, `(`, `)`, `\`, NUL), not LDAP **DN** metacharacters (`,`, `+`, `"`, `<`, `>`, `;`, `=`, leading `#`/space). Because the wrong escaping context is applied, an unauthenticated client submitting a login request can inject additional RDN/DN components into the bind string sent to the upstream LDAP server.

### Finding Description
`CreateSession` is reachable directly from the unauthenticated public login endpoint `POST /sessions`, which parses the request body into `sessions.SessionRequest{Email, Password}` and forwards it unmodified to the configured `AuthenticationProvider`: [1](#0-0) 

When the LDAP authenticator is configured, `CreateSession` constructs the bind DN like this: [2](#0-1) 

`TestPassword` does the same thing: [3](#0-2) 

In both cases, `ldap.EscapeFilter` (from `github.com/go-ldap/ldap/v3`) is applied to the attacker-supplied `email`/`username` value and the result is embedded directly into a DN string via `fmt.Sprintf("%s=%s,%s,%s", BaseUserAttr, escapedEmail, UsersDN, BaseDN)`. `EscapeFilter` only escapes characters meaningful in LDAP *search filter* syntax; it does not escape DN-reserved characters such as comma, plus, double-quote, semicolon, or leading `#`/space. This mismatch means a client-supplied email such as `foo,ou=SomeOtherOU,dc=example,dc=com` (or values containing `+`, `"`, etc.) is inserted verbatim into the bind DN, altering its structure and letting the caller influence which DN component boundaries are formed before the fixed `UsersDN`/`BaseDN` suffix is appended.

This directly mirrors the CVE-2019-12736 bug class: user-supplied input meant for a "username" field is not sanitized for the LDAP protocol (DN context), enabling LDAP DN injection — the LDAP analog of command/query injection.

By contrast, the same `escapedEmail` value is correctly used for filter-context queries (in `FindUser` and `validateUsersActive`), showing the escaping mechanism was intended for filters, not for DN construction: [4](#0-3) 

### Impact Explanation
An unprivileged, unauthenticated caller of the public `/sessions` login endpoint controls the string that becomes part of the LDAP Bind DN sent to the upstream directory server. Depending on the upstream LDAP server's schema and how permissively it parses malformed/injected DNs, this can be leveraged to target unintended directory entries or otherwise manipulate the bind target used for authentication — an authentication-adjacent request-impersonation/DN-confusion primitive reachable from a completely unauthenticated node API request. Successful exploitation could subvert the authentication decision path that governs which Chainlink RBAC role (`Admin`, `Edit`, `Run`, `Read`) is subsequently granted.

### Likelihood Explanation
Exploitability depends on the operator having `WebServer.AuthenticationMethod = 'ldap'` configured and on the target LDAP server's DN parsing behavior and directory layout, so it is not universally exploitable out-of-the-box; however, the attack requires no privileges or existing credentials — only a crafted `email` field in an anonymous login POST request — and the injection point is present unconditionally in the code whenever LDAP auth is enabled.

### Recommendation
Do not reuse `ldap.EscapeFilter` for DN construction. Use a proper DN-escaping routine (e.g., escape `,+"\<>;` and leading `#`/space per RFC 4514, or build the DN using a dedicated DN-builder API) for the `escapedEmail`/username value used in `conn.Bind(searchBaseDN, ...)` calls in both `CreateSession` and `TestPassword`. Reserve `ldap.EscapeFilter` only for values embedded in LDAP search filters (as already correctly done in `FindUser`/`validateUsersActive`). Additionally consider validating/normalizing the email format before using it in any LDAP protocol string.

### Proof of Concept
1. Configure a Chainlink node with `WebServer.AuthenticationMethod = 'ldap'` and valid `WebServer.LDAP` settings.
2. Send an unauthenticated POST to `/sessions` with a crafted email containing DN metacharacters not covered by `ldap.EscapeFilter`, e.g.:
```
POST /sessions
{"email": "user,ou=Admins,dc=example,dc=com", "password": "attacker-controlled"}
```
3. Observe in `CreateSession` (`core/sessions/ldapauth/ldap.go:406-408`) that `searchBaseDN` becomes `uid=user,ou=Admins,dc=example,dc=com,ou=users,dc=custom,dc=example,dc=com` — the comma in the supplied email is not escaped, altering the intended DN structure that is sent to `conn.Bind`, demonstrating the injection point. [5](#0-4)

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

**File:** core/sessions/ldapauth/ldap.go (L154-164)
```go
	escapedEmail := ldap.EscapeFilter(email)
	searchBaseDN := fmt.Sprintf("%s, %s", l.config.GroupsDN(), l.config.BaseDN())
	filterQuery := fmt.Sprintf("(&(uniquemember=%s=%s,%s,%s))", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	searchRequest := ldap.NewSearchRequest(
		searchBaseDN,
		ldap.ScopeWholeSubtree, ldap.NeverDerefAliases,
		0, int(l.config.QueryTimeout().Seconds()), false,
		filterQuery,
		[]string{"cn"},
		nil,
	)
```

**File:** core/sessions/ldapauth/ldap.go (L405-411)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L511-514)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
```
