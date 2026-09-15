## Analysis

The external report describes CVE-2022-31088: unauthenticated LDAP injection via the login username field in LDAP Account Manager, allowing LDAP data enumeration because user input was placed into an LDAP query/filter without correct escaping for that context.

I found a directly analogous root-cause pattern in chainlink's LDAP authentication driver, which is reachable by any unauthenticated client hitting the login endpoint.

### Title
Unauthenticated LDAP DN injection via login email in LDAP bind construction - (`core/sessions/ldapauth/ldap.go`)

### Summary
The LDAP authentication provider's `CreateSession` and `TestPassword` methods build an LDAP **Distinguished Name (DN)** for `conn.Bind()` by concatenating the user-supplied login email into a DN string, but only apply `ldap.EscapeFilter()` — which escapes RFC4515 **search filter** metacharacters, not RFC4514 **DN** metacharacters — before insertion.

### Finding Description
In `CreateSession`, the email from the unauthenticated `SessionRequest` (posted to `/sessions` via `SessionsController.Create`) is filter-escaped and then interpolated directly into a bind DN string: [1](#0-0) 

The same pattern recurs in `TestPassword`: [2](#0-1) 

`ldap.EscapeFilter` only escapes `*`, `(`, `)`, `\`, and NUL — the special characters for LDAP *search filters* (RFC4515). It does **not** escape DN special characters such as `,`, `+`, `"`, `\`, `<`, `>`, `;`, `=`, or leading/trailing spaces (RFC4514). Since `searchBaseDN` is used as a literal DN in `conn.Bind(searchBaseDN, sr.Password)`, an attacker who controls the `email` field of the login request can inject additional RDN components or alter the DN structure, changing which directory object the bind is actually attempted against. The entry point (`SessionsController.Create` → `AuthenticationProvider().CreateSession`) requires no prior authentication: [3](#0-2) [4](#0-3) 

The correctly-scoped filter query in `FindUser`/`validateUsersActive`, by contrast, uses `EscapeFilter` in an actual filter context, which is appropriate: [5](#0-4) 
This confirms the bug is specifically the context mismatch — filter-escaping applied to DN construction — in the bind paths.

### Impact Explanation
An unprivileged, unauthenticated client submitting a crafted `email` value to `/sessions` can manipulate the DN passed to the LDAP `Bind` call. Depending on the directory layout and LDAP server behavior, this can be leveraged to bind against unintended objects, probe directory structure, or influence authentication outcome/errors, mirroring the enumeration/injection impact described in the source CVE (LDAP search-configuration abuse via the login field). This directly touches the node's authentication boundary (`sessions.AuthenticationProvider` / `web/auth`), so any bypass or information leak here has outsized impact relative to a normal input validation bug.

### Likelihood Explanation
Likelihood is moderate: exploitation requires the node to be configured with the LDAP authentication driver (`config.LDAP` enabled) and depends on the target LDAP server's handling of malformed/unexpected DNs, and on the directory's `UsersDN`/`BaseDN` structure. No authentication or special privilege is required to send the request — only network access to the node's `/sessions` endpoint.

### Recommendation
- Use a proper DN-escaping function (e.g., `ldap.EscapeDN` if available in the `go-ldap/v3` version in use, or manually escape `,+"\<>;=` and leading/trailing spaces per RFC4514) when constructing `searchBaseDN` in `CreateSession` and `TestPassword`, instead of reusing `ldap.EscapeFilter`.
- Alternatively, avoid DN string concatenation altogether and perform an LDAP *search* for the user's DN using a properly filter-escaped query, then bind using the resolved DN returned by the directory rather than a manually constructed one.
- Add regression tests asserting that emails containing DN metacharacters (`,`, `+`, `"`, `=`, etc.) are rejected or safely escaped before use in `Bind`.

### Proof of Concept
1. Configure a node with the LDAP authentication driver enabled against a test LDAP directory.
2. POST to `/sessions` with a JSON body such as:
   ```json
   {"email": "victim,dc=example,dc=com", "password": "anything"}
   ```
3. Observe that `escapedEmail` passes through `ldap.EscapeFilter` unchanged for the comma (since `,` is not a filter metacharacter), producing a `searchBaseDN` like:
   `uid=victim,dc=example,dc=com,ou=users,dc=example,dc=com`
   — altering the intended bind target DN rather than the literal supplied email, demonstrating that attacker-controlled DN components are injected into the `conn.Bind` call.

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

**File:** core/sessions/ldapauth/ldap.go (L511-518)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
	if err == nil {
		return nil
	}
	l.lggr.Infof("Error binding user authentication request in TestPassword call LDAP Bind: %v", err)
```

**File:** core/web/sessions_controller.go (L29-39)
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
```

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```
