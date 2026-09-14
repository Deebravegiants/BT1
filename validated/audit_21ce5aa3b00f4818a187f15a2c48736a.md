The chainlink LDAP authentication adapter at `core/sessions/ldapauth/ldap.go` has essentially the same bug class as the reported parse-server CVE: DN components are built from unsanitized/incorrectly-escaped user input.

### Title
LDAP DN injection via `ldap.EscapeFilter` misuse when constructing bind DN and search-base DN strings - (File: core/sessions/ldapauth/ldap.go)

### Summary
User-supplied email (`sr.Email` on the login endpoint, and the `email` parameter of `TestPassword`/`FindUser`) is escaped only with `ldap.EscapeFilter` and then concatenated directly into LDAP Distinguished Name (DN) strings that are subsequently used as the bind DN or search base DN. `EscapeFilter` implements RFC 4515 filter-value escaping (escaping `(`, `)`, `\`, `*`, NUL) — it does **not** escape RFC 4514 DN-structural characters such as `,`, `+`, `"`, `<`, `>`, `;`. Because these DN metacharacters pass through unescaped, an attacker-controlled email value can inject additional RDN components into the DN used for LDAP `Bind`/`Search`, exactly analogous to the parse-server LDAP-injection advisory (GHSA-7m6r-fhh7-r47c), which stems from unescaped interpolation into DN and filter strings.

### Finding Description
In `CreateSession` (the unauthenticated login handler) and `TestPassword`, the code does: [1](#0-0) 
```go
escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
```
`searchBaseDN` is passed as the bind DN itself, not as a filter value, so it is parsed by the LDAP server as a structured DN string (RFC 4514), not as a filter expression (RFC 4515). `ldap.EscapeFilter` escapes the wrong character set for this context — it does not escape `,`/`+`/`"`/`<`/`>`/`;`, which are the characters that structurally delimit RDNs in a DN. The identical pattern recurs in `TestPassword`: [2](#0-1) 
and in `FindUser`, where a DN-like string is built into the filter value: [3](#0-2) 

The connection used for these operations is bootstrapped via `CreateEphemeralConnection`, which itself builds the read-only service bind DN with plain string concatenation (not user input, so lower risk): [4](#0-3) 

### Impact Explanation
An attacker submitting a crafted `email` value (e.g. containing a comma to append extra RDN components, such as `attacker,dc=example,dc=com` or similar constructs) to the unauthenticated `/sessions` login endpoint can alter the DN structure that `conn.Bind` attempts to authenticate against. Depending on the directory layout and how permissively the LDAP server resolves malformed/injected DNs, this could allow probing or binding against unintended DN paths, or interfering with the intended entry lookup — mirroring the parse-server advisory's core issue of DN injection enabling authentication/authorization manipulation. Because chainlink's LDAP roles (`Admin`/`Edit`/`Run`/`View`) are derived purely from LDAP group membership resolved through DN/filter strings built the same insecure way (see `FindUser`, `validateUsersActive`, `ldapGroupMembersListToUser`), any DN manipulation in this path has a direct bearing on node RBAC role assignment.

### Likelihood Explanation
This code path is reachable directly from the unauthenticated login request (`CreateSession`) with attacker-fully-controlled `sr.Email` field, requiring no pre-existing chainlink session — only that an LDAP backend is configured (`ldapAuthenticator`, see `NewLDAPAuthenticator`). No special network position or operator privilege is needed to submit the crafted email; only a request to the standard session-creation endpoint. This aligns with the CWE-90 (LDAP injection) classification and the "unprivileged-actor" scope of the requested analog.

### Recommendation
Use a proper RFC 4514 DN-escaping routine (escaping `,`, `+`, `"`, `\`, `<`, `>`, `;`, leading/trailing spaces, and leading `#`) for any user-supplied value interpolated into a DN string (`searchBaseDN` in `CreateSession`, `TestPassword`, and the DN-like `uniquemember=...` value built in `FindUser`). `ldap.EscapeFilter` should be reserved strictly for values placed inside filter expressions per RFC 4515; it must not be relied upon to sanitize DN components. The `go-ldap/ldap/v3` library does not currently expose a "EscapeDN"-equivalent helper as far as this code uses it, so an explicit DN-escaping helper should be implemented and applied everywhere `l.config.BaseUserAttr()+"="+userInput` style DN construction occurs.

### Proof of Concept
1. Configure chainlink with LDAP auth enabled (`ldapCfg`), pointing at any directory server, with `BaseUserAttr=uid`, `UsersDN=ou=users`, `BaseDN=dc=example,dc=com`.
2. Send a login request to the session-creation endpoint with:
   - `email = "victim,ou=admins,dc=example,dc=com"` (or another DN-breaking payload using `,`/`+`)
   - any password
3. Observe that `searchBaseDN` in `CreateSession`/`ldap.go` line 407 becomes `uid=victim,ou=admins,dc=example,dc=com,ou=users,dc=example,dc=com` — the unescaped comma injects an additional RDN segment (`ou=admins,...`) into the DN handed to `conn.Bind`, demonstrating that attacker input controls DN structure rather than being confined to a single attribute value, matching the DN-injection root cause described in the advisory.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L154-156)
```go
	escapedEmail := ldap.EscapeFilter(email)
	searchBaseDN := fmt.Sprintf("%s, %s", l.config.GroupsDN(), l.config.BaseDN())
	filterQuery := fmt.Sprintf("(&(uniquemember=%s=%s,%s,%s))", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
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

**File:** core/sessions/ldapauth/client.go (L32-42)
```go
func (l *ldapClient) CreateEphemeralConnection() (LDAPConn, error) {
	conn, err := ldap.DialURL(l.config.ServerAddress())
	if err != nil {
		return nil, fmt.Errorf("failed to Dial LDAP Server: %w", err)
	}
	// Root level root user auth with credentials provided from config
	bindStr := l.config.BaseUserAttr() + "=" + l.config.ReadOnlyUserLogin() + "," + l.config.BaseDN()
	if err := conn.Bind(bindStr, l.config.ReadOnlyUserPass()); err != nil {
		return nil, fmt.Errorf("unable to login as initial root LDAP user: %w", err)
	}
	return conn, nil
```
