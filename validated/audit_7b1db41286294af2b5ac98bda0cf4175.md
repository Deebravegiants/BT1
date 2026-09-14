Confirmed: the login endpoint `SessionsController.Create` in `core/web/sessions_controller.go` is unauthenticated and binds the raw JSON body directly into `clsessions.SessionRequest{Email, Password}` before calling `AuthenticationProvider().CreateSession(ctx, sr)`. This flows into the LDAP authenticator's DN construction with only filter-escaping applied to a value used in a DN context — a mismatch analogous to the DN/space-handling parsing flaw class in CVE-2020-27840.

### Title
LDAP DN injection via unescaped `email` field in bind/search DN construction - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The `go-ldap` `ldap.EscapeFilter()` function only escapes characters that are special in LDAP *search filters* (`(`, `)`, `*`, `\`, NUL). It does **not** escape characters that are special in LDAP *distinguished names* (DN), such as `,`, `+`, `"`, `<`, `>`, `;`, `=`, and leading/trailing spaces. `ldapAuthenticator.CreateSession` and `TestPassword` use `EscapeFilter`-escaped user-supplied email to build a raw DN string, then pass it directly to `conn.Bind()`.

### Finding Description
`CreateSession` (unprivileged, unauthenticated caller via `POST /sessions`) takes `sr.Email` from `core/web/sessions_controller.go:35-56`, escapes it only for filter context, and builds the bind DN: [1](#0-0) 
The same pattern occurs in `TestPassword`: [2](#0-1) 
`ldap.EscapeFilter` is designed for RFC 4515 filter escaping, not RFC 4514 DN escaping — DN metacharacters like `,` are not escaped by it. Because the resulting string is used as the actual **Bind DN** (not a filter), an attacker-supplied email containing a comma (e.g. `foo,ou=AdminUsers,dc=custom,dc=example,dc=com` or similar DN suffix injections) can alter the effective DN structure passed to `conn.Bind()`, changing which directory entry the bind attempt targets rather than merely being escaped as literal filter text. This is the same underlying bug class as CVE-2020-27840: DN string components (here, attacker-controlled email) are inserted into a DN without DN-appropriate escaping/handling of DN metacharacters, producing DN parsing/structure corruption instead of an inert string comparison.

### Impact Explanation
An unauthenticated caller controls the `Email` field of the login request and can inject DN-structural characters into the bind DN used against the upstream LDAP directory. Depending on directory layout this can be used to probe or manipulate which DN is targeted by an authentication bind, enabling authentication-bind confusion/request impersonation against the LDAP backend. This directly affects the internet-facing node login path (`core/web/sessions_controller.go`), which is unauthenticated by design (login endpoint).

### Likelihood Explanation
Reachable trivially and pre-authentication: any unauthenticated caller can POST a crafted `email` value to `/sessions`. The only requirement for real-world exploitation is that `AuthenticationMethod = 'ldap'` is enabled (an opt-in feature), which limits blast radius to nodes explicitly configured for LDAP auth, but the code path itself is unconditionally reachable pre-auth on those nodes.

### Recommendation
Use a proper DN-escaping function (e.g. `go-ldap`'s DN escaping helper, or manually escape `,`, `+`, `"`, `\`, `<`, `>`, `;`, `=`, and leading/trailing spaces per RFC 4514) instead of `EscapeFilter` whenever building DN strings (`CreateSession`, `TestPassword`, and any other `fmt.Sprintf("...%s...")` DN construction in `core/sessions/ldapauth/ldap.go`). Filter-context strings (used in `filterQuery`) should keep `EscapeFilter`; DN-context strings need separate, correct DN escaping.

### Proof of Concept
1. Configure a node with `WebServer.AuthenticationMethod = 'ldap'` and a `WebServer.LDAP.BaseDN`/`UsersDN` per `docs/CONFIG.md`. [3](#0-2) 
2. POST to the login endpoint with an `email` value containing DN metacharacters not covered by `EscapeFilter`, e.g. `uid=x,ou=SomeOtherOU,dc=custom,dc=example,dc=com` (or a value with an embedded comma to break out of the intended `uid=<email>,ou=users,...` DN).
3. Observe that `searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())` at [4](#0-3)  constructs a DN different from the intended `uid=<attacker>,ou=users,dc=...` structure, since `escapedEmail` passes through unescaped for DN-special characters.

<br>

Note: I was unable to fully trace whether the underlying LDAP server/library would reject malformed DNs outright versus silently mis-binding, since that depends on the external LDAP server's own DN parser — the codebase index does not include a live LDAP server to test against. The core issue (wrong escaping function used for DN vs filter context) is confirmed by direct code inspection.

### Citations

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

**File:** docs/CONFIG.md (L663-672)
```markdown
## WebServer.LDAP
```toml
[WebServer.LDAP]
ServerTLS = true # Default
SessionTimeout = '15m0s' # Default
QueryTimeout = '2m0s' # Default
BaseUserAttr = 'uid' # Default
BaseDN = 'dc=custom,dc=example,dc=com' # Example
UsersDN = 'ou=users' # Default
GroupsDN = 'ou=groups' # Default
```
