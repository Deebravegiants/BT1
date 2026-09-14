## Analysis

The reachable analog to CVE‑2023‑51446 ("LDAP injection during authentication") in this codebase is in the LDAP authentication provider's session/password-verification bind-DN construction.

### Title
LDAP DN injection in authentication bind construction using filter-escaping instead of DN-escaping - (File: core/sessions/ldapauth/ldap.go)

### Summary
`ldapAuthenticator.CreateSession` and `ldapAuthenticator.TestPassword` build the LDAP Bind Distinguished Name (DN) by concatenating the unprivileged, client-supplied `email` value with configured DN fragments, escaping the email with `ldap.EscapeFilter` before use. [1](#0-0) [2](#0-1)  `ldap.EscapeFilter` only escapes characters that are special in LDAP *search filters* (`(`, `)`, `\`, `*`, NUL) — it does not escape characters that are structurally significant in an LDAP *Distinguished Name* (`,`, `+`, `"`, `<`, `>`, `;`, `=`, leading `#`/space). Since the resulting string is passed directly as a DN to `conn.Bind(searchBaseDN, password)`, this is DN construction, not filter construction, and the wrong escaping routine is applied.

### Finding Description
An unprivileged client submits credentials to the `/sessions` login endpoint, which is dispatched to the configured `AuthenticationProvider`. When `WebServer.AuthenticationMethod` is `ldap`, `sessions.LDAPAuth` routes to `ldapauth.NewLDAPAuthenticator`, whose `CreateSession` handles the login request. [3](#0-2)  The `sr.Email` field of the login request (fully attacker-controlled, unauthenticated) is lower-cased, passed through `ldap.EscapeFilter`, and interpolated into a DN string template:

```go
escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
if err = conn.Bind(searchBaseDN, sr.Password); err != nil { ... }
``` [4](#0-3) 

The identical unsafe pattern exists in `TestPassword`, which is also reachable for credential verification (e.g. password-change confirmation flows):
```go
escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
err = conn.Bind(searchBaseDN, password)
``` [5](#0-4) 

Because `EscapeFilter` does not neutralize DN metacharacters such as `,` or `+`, an attacker-supplied email value containing these characters can alter the structure of the DN passed to `Bind`, causing the LDAP client to attempt binding against a different/attacker-chosen DN than the one intended by `BaseUserAttr`/`UsersDN`/`BaseDN`. This is the same bug class as CVE-2023-51446: user-controlled authentication-form input is inserted into an LDAP query/DN construct without the correct context-specific escaping.

By contrast, the search-filter code paths in the same file (`FindUser`, `validateUsersActive`) correctly use `EscapeFilter` because they build filter *values*, not DNs. [6](#0-5)  The bug is specific to the two Bind-DN construction sites.

### Impact Explanation
If the target LDAP directory permits multi-valued/ambiguous RDN parsing, or if the attacker can append additional RDN components (e.g., via `,` injection) that resolve to an existing DN, an unauthenticated client could manipulate which directory entry the server attempts to bind against during `CreateSession`. Combined with the `localLoginFallback` behavior (which is also triggered on bind failure) this expands the attack surface of the authentication endpoint to directory-structure-dependent DN confusion, a recognized LDAP injection impact class (authentication bypass / cross-account bind confusion) rather than a purely cosmetic issue. Exact exploitability depends on the specific LDAP server's DN parsing tolerance, which is external and not verifiable from this repo alone — but the root cause (wrong escaping function for the DN context) is concretely present in the code.

### Likelihood Explanation
The vulnerable code paths (`CreateSession`, `TestPassword`) are on the primary unauthenticated login path (`POST /sessions`) whenever `WebServer.AuthenticationMethod = 'ldap'` is configured, making the reachable attacker any unauthenticated network client able to submit a login request with an arbitrary `email` field. [3](#0-2) 

### Recommendation
Replace `ldap.EscapeFilter` with a proper DN-escaping routine (e.g. RFC 4514 DN escaping, or use the `go-ldap` library's DN-building helpers such as `ldap.EscapeDN`/manual escaping of `,+"\<>;=` and leading `#`/space) at both call sites in `CreateSession` and `TestPassword` before interpolating `email` into the bind DN string.

### Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `BaseUserAttr = 'uid'`, `UsersDN = 'ou=users'`, `BaseDN = 'dc=example,dc=com'`.
2. Send `POST /sessions` with a JSON body containing an `email` value crafted with embedded DN metacharacters, e.g. `uid=victim,ou=users,dc=example,dc=com` as the `email` field itself (comma is not escaped by `EscapeFilter`), producing a bind DN of `uid=uid=victim,ou=users,dc=example,dc=com,ou=users,dc=example,dc=com`.
3. Depending on the target LDAP server's DN-parsing behavior, this malformed/injected DN string can be interpreted in unexpected ways at bind time, since none of the injected DN-structural characters were sanitized — demonstrating the missing DN escaping at [4](#0-3) .

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

**File:** core/sessions/ldapauth/ldap.go (L404-411)
```go

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L510-514)
```go

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
```

**File:** core/services/chainlink/application.go (L588-596)
```go
	switch sessions.AuthenticationProviderName(authMethod) {
	case sessions.LDAPAuth:
		var err error
		authenticationProvider, err = ldapauth.NewLDAPAuthenticator(
			opts.DS, cfg.WebServer().LDAP(), cfg.Insecure().DevWebServer(), globalLogger, auditLogger,
		)
		if err != nil {
			return nil, errors.Wrap(err, "NewApplication: failed to initialize LDAP Authentication module")
		}
```
