Audit Report

## Title
LDAP DN injection in authentication bind construction using filter-escaping instead of DN-escaping - (File: core/sessions/ldapauth/ldap.go)

## Summary
`ldapAuthenticator.CreateSession` builds the LDAP Bind DN by concatenating the attacker-controlled, unauthenticated `sr.Email` field with configured DN fragments (`BaseUserAttr`, `UsersDN`, `BaseDN`), but escapes the email using `ldap.EscapeFilter`, which only neutralizes LDAP *search filter* metacharacters (`(`, `)`, `\`, `*`, NUL) rather than LDAP *Distinguished Name* metacharacters (`,`, `+`, `"`, `<`, `>`, `;`, `=`, leading `#`/space). [1](#0-0)  The same flawed pattern exists in `TestPassword`. [2](#0-1) 

## Finding Description
The `POST /sessions` endpoint, when `WebServer.AuthenticationMethod = 'ldap'`, dispatches to `ldapauth.NewLDAPAuthenticator`, whose `CreateSession` is invoked with the fully unauthenticated, client-controlled `sessions.SessionRequest.Email` field. [3](#0-2)  Inside `CreateSession`, the email is lower-cased, passed through `ldap.EscapeFilter`, and interpolated directly into a DN template that is passed to `conn.Bind(searchBaseDN, sr.Password)`:
```go
escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
if err = conn.Bind(searchBaseDN, sr.Password); err != nil { ... }
``` [4](#0-3) 

`EscapeFilter` is designed for LDAP search-filter *value* contexts (as correctly used elsewhere in the same file for building `filterQuery` values passed to `ldap.NewSearchRequest`) [5](#0-4) , not for DN construction. Because `,`/`+`/`=` and other RDN-structural characters are left unescaped, a crafted `email` value can inject additional RDN components into the Bind DN string, altering which directory entry `conn.Bind` attempts to authenticate against — the same root-cause class as CVE-2023-51446 (wrong escaping routine applied to a DN-construction context). No other validation intercepts this: `sr.Email` is only lower-cased before being escaped with the wrong function, and there is no allowlist/format check on the email field prior to DN construction.

The identical pattern exists in `TestPassword`: [6](#0-5) . However, unlike `CreateSession`, `TestPassword`'s `email` argument is always supplied internally by the caller as the already-authenticated session user's own email (`sessionUser.Email` from `webauth.GetAuthenticatedUser(c)`), not attacker-supplied at the HTTP layer. [7](#0-6)  Thus `TestPassword`'s reachable injection surface is limited to a value already fixed by a prior authenticated identity, not directly attacker-chosen input, making `CreateSession` the primary reachable instance.

## Impact Explanation
This is a real root-cause bug: the wrong escaping function (`EscapeFilter`) is applied to a Bind DN string built from unauthenticated client input, which is the same defect class as CVE-2023-51446. If the target LDAP server's DN parser tolerates the injected structural characters, the attacker-controlled `email` field could alter which DN the server binds to during authentication, falling under the "node API authentication bypass" impact category. This maps to an in-scope Chainlink impact class.

## Likelihood Explanation
The vulnerable `CreateSession` path is on the unauthenticated `POST /sessions` login endpoint whenever `WebServer.AuthenticationMethod = 'ldap'` is configured, so any unauthenticated network client can supply an arbitrary `email` value and repeatedly attempt the injection. [3](#0-2)  This requires no privileged credentials or host access to trigger.

## Recommendation
Replace `ldap.EscapeFilter` with proper RFC 4514 DN escaping (escaping `,+"\<>;=` and leading `#`/space, e.g. via a dedicated DN-escaping helper) at the DN-construction call sites in `CreateSession` (core/sessions/ldapauth/ldap.go:406-407) and `TestPassword` (core/sessions/ldapauth/ldap.go:512-513), keeping `EscapeFilter` only for the actual filter-value use sites such as `FindUser`/`validateUsersActive`.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `BaseUserAttr = 'uid'`, `UsersDN = 'ou=users'`, `BaseDN = 'dc=example,dc=com'`, against a real/test LDAP directory server.
2. Send `POST /sessions` with `email` set to a value containing an unescaped comma/RDN sequence, e.g. `email: "uid=victim,ou=users,dc=example,dc=com"`.
3. Observe that `ldap.EscapeFilter` leaves the comma unescaped, producing bind DN `uid=uid=victim,ou=users,dc=example,dc=com,ou=users,dc=example,dc=com` passed to `conn.Bind`, confirming the DN is attacker-influenced structurally rather than treated as an opaque `uid` value. This can be validated with a Go unit test asserting `ldap.EscapeFilter` does not escape `,`/`+`/`=` and that the resulting `searchBaseDN` string in `CreateSession` contains attacker-injected RDN components.

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

**File:** core/web/user_controller.go (L252-268)
```go
	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to create API token"))
		return
	}
	// In order to create an API token, login validation with provided password must succeed
	err = u.App.AuthenticationProvider().TestPassword(ctx, sessionUser.Email, request.Password)
```
