## Finding: LDAP DN Injection via unescaped user-supplied email in Bind DN construction

The chainlink LDAP authenticator has the same underlying bug class as the reported Derby CVE-2022-46337: user-supplied credentials are used to build an LDAP query/DN string using the wrong escaping function for the context, allowing a crafted "username" (email) to manipulate the structure of the distinguished name used for authentication.

### Title
LDAP DN injection in `CreateSession`/`TestPassword` due to filter-escaping (not DN-escaping) of attacker-controlled email - (File: `core/sessions/ldapauth/ldap.go`)

### Summary
The `POST /sessions` login endpoint is reachable by any unauthenticated client and forwards the submitted email directly into an LDAP Bind DN. The code escapes the email with `ldap.EscapeFilter`, which is designed to sanitize values for RFC 4515 *search filters* (`*`, `(`, `)`, `\`, NUL), not RFC 4514 *distinguished names* (`,`, `+`, `"`, `<`, `>`, `;`, `=`, leading/trailing spaces). Using filter-escaping in a DN-construction context leaves DN metacharacters like `,` unescaped.

### Finding Description
In `CreateSession`, the attacker-controlled `sr.Email` from the public session-creation request is only filter-escaped before being spliced into the bind DN string: [1](#0-0) 

The same pattern repeats in `TestPassword`: [2](#0-1) 

Because `ldap.EscapeFilter` does not escape `,` (the RDN separator in a DN), a value such as `alice,ou=SomeOtherOU` injected into the email field alters the number/structure of RDN components that `conn.Bind()` will attempt to authenticate against, rather than the single intended `uid=<email>` component. This is invoked from the public, unauthenticated HTTP endpoint: [3](#0-2) 

which calls into `AuthenticationProvider().CreateSession(ctx, sr)` — reachable pre-auth by design.

The correct fix in the upstream `go-ldap` ecosystem and in general LDAP-consuming code is to use a DN-specific escaping routine (e.g. `ldap.EscapeDN` in newer go-ldap versions, or manual RFC 4514 escaping) whenever a value is concatenated into a DN, and reserve `EscapeFilter` strictly for values placed inside search filters (as is correctly done in `FindUser`'s `filterQuery` construction and `validateUsersActive`): [4](#0-3) [5](#0-4) 

### Impact Explanation
The Bind DN sent to the upstream LDAP server is not the value the operator intended — an unprivileged, unauthenticated caller controls part of the DN structure that gets bound. Depending on the LDAP directory's tree layout and how permissively the server resolves DNs, this can enable authentication requests to be targeted at unintended directory entries, undermining the integrity of the identity check that `CreateSession`/`TestPassword` are meant to enforce. This is the direct analog of the Derby advisory: a crafted username string subverts the intended authentication-target resolution logic in an LDAP-backed authenticator.

### Likelihood Explanation
The vector is fully reachable by any unauthenticated actor hitting `POST /sessions` (login) with an arbitrary `email` field; no privileges or prior session are required. Exploitability of a concrete bypass depends on the specific LDAP directory's DN layout (whether crafted RDN chains resolve to any real, unintended entry), so likelihood is moderate-to-high for information/structure probing and directory-dependent for full impersonation.

### Recommendation
Replace `ldap.EscapeFilter` with a DN-appropriate escaping function everywhere an attacker-controlled value is concatenated into a bind DN or search base DN (`CreateSession`, `TestPassword`, and the `searchBaseDN`/`bindStr` construction sites in `core/sessions/ldapauth/ldap.go` and `core/sessions/ldapauth/client.go`). Keep `EscapeFilter` only for values placed inside LDAP filter expressions (as already done for the `uniquemember=...` filter). Additionally, validate/reject emails containing DN metacharacters (`,`, `+`, `"`, `<`, `>`, `;`, `=`) before using them in any DN context, as defense in depth.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `BaseUserAttr = 'uid'`, `UsersDN = 'ou=users'`, `BaseDN = 'dc=example,dc=com'`.
2. Send an unauthenticated `POST /sessions` request:
```json
{"email": "victim,ou=someOtherOU,dc=example,dc=com", "password": "guess"}
```
3. `core/sessions/ldapauth/ldap.go` `CreateSession` builds:
```
searchBaseDN = "uid=victim,ou=someOtherOU,dc=example,dc=com,ou=users,dc=example,dc=com"
```
instead of the intended `uid=victim,ou=users,dc=example,dc=com`, demonstrating that the comma in the email field is not neutralized and alters the DN structure passed to `conn.Bind()`.

### Citations

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

**File:** core/sessions/ldapauth/ldap.go (L666-671)
```go
	filterQuery := "(|"
	for _, email := range emails {
		escapedEmail := ldap.EscapeFilter(email)
		filterQuery = fmt.Sprintf("%s(%s=%s)", filterQuery, l.config.BaseUserAttr(), escapedEmail)
	}
	filterQuery = fmt.Sprintf("(&%s))", filterQuery)
```

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
