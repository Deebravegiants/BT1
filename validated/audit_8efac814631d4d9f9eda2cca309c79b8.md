## Finding

### Title
LDAP Bind-DN injection via unsanitized email in `CreateSession`/`TestPassword` (missing DN-encoding of user-supplied login email) - (File: `core/sessions/ldapauth/ldap.go`)

### Summary
CVE-2023-29050 describes an LDAP-provider bug class where user-controlled fragments were embedded into LDAP query strings without correct encoding, allowing an attacker to escape the intended directory hierarchy. The Chainlink node's LDAP authentication driver has an analogous flaw: the unauthenticated login endpoint (`POST /sessions`) constructs the LDAP **Bind DN** from the client-supplied `email` field using `ldap.EscapeFilter()`, which only escapes RFC 4515 *filter* metacharacters and does **not** escape RFC 4514 *Distinguished Name* metacharacters (comma, `+`, `"`, `<`, `>`, `;`, leading `#`/space). Because the escaped value is spliced directly into a DN string rather than a filter, an attacker-controlled comma is not neutralized and can alter the RDN structure of the DN sent in the LDAP `Bind` request.

### Finding Description
In `CreateSession` (login handler for the `ldap` authentication method): [1](#0-0) 

`sr.Email` is fully attacker-controlled (submitted via the unauthenticated `POST /sessions` request body, confirmed by the HTTP-level test at [2](#0-1) ). It is passed through `ldap.EscapeFilter`, which escapes only `\`, `*`, `(`, `)`, and NUL — the metacharacters relevant to LDAP *search filter* syntax (RFC 4515). The result is then concatenated with `,` into a `Bind` DN:

```go
escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
conn.Bind(searchBaseDN, sr.Password)
```

The same pattern recurs in `TestPassword`: [3](#0-2) 

Because DN structure is delimited by unescaped commas (per RFC 4514), a client-supplied email containing a comma (e.g. `uid=victim,ou=admins,dc=example,dc=com`-shaped input, or simply an email with an embedded `,ou=...` suffix) is not neutralized by `EscapeFilter` and is passed to the underlying `go-ldap` `Bind` call as literal DN structure, letting the client influence which RDN components the server parses out of the target bind name. This is the same root-cause class as CVE-2023-29050: a security-relevant LDAP-query fragment (here, the bind target rather than a search filter) is built from unprivileged user input without the encoding appropriate to the context it's placed in (DN context vs. filter context).

This is reachable by a completely unauthenticated client: the `/sessions` endpoint is the login route itself, so no prior authentication or privilege is required to exercise the flawed code path, satisfying the "unprivileged actor... session/token handling" scope.

### Impact Explanation
Exact exploitability depends on the target LDAP server's DN-parsing/normalization behavior, but the structural flaw allows an unauthenticated client to inject additional RDN components into the DN used for authentication binds, breaking the intended containment to `BaseUserAttr=<email>,<UsersDN>,<BaseDN>`. Depending on server behavior this can enable directory traversal outside the intended `UsersDN` subtree for bind attempts, produce confusing/erroneous authentication results that leak directory structure, or (in combination with servers that treat malformed/attacker-shaped bind names permissively) increase the attack surface for authentication confusion. This aligns with the CVE's stated impact of breaking confidentiality/hierarchy boundaries of the directory from an unprivileged actor.

### Likelihood Explanation
High reachability: any unauthenticated client can submit an arbitrary `email` value to `POST /sessions` with the LDAP authentication method configured (a supported, documented production configuration per `core/config/docs/core.toml`). No privileges or prior session are needed to reach `CreateSession`/`TestPassword`. Successful practical exploitation further depends on the specific LDAP server's DN parsing/ACL behavior, but the code-level defect (wrong escaping function used for a DN context) is unambiguous and directly attacker-triggerable.

### Recommendation
- Use a DN-aware escaping function (RFC 4514) — e.g. `go-ldap`'s `ldap.EscapeDN`/equivalent, or reject/validate the email against a strict allow-list character set — before embedding `sr.Email` into `searchBaseDN` in both `CreateSession` and `TestPassword`.
- Continue using `ldap.EscapeFilter` only for values placed inside filter expressions (as is already correctly done in `FindUser` and `validateUsersActive`), and never reuse a filter-escaped value for DN construction.
- Add regression tests submitting emails containing `,`, `+`, `"`, and leading `#`/space to confirm the resulting Bind DN is not structurally altered.

### Proof of Concept
1. Configure the node with `WebServer.AuthenticationMethod = 'ldap'`.
2. Send `POST /sessions` with body `{"email":"attacker@example.com,ou=admins,dc=example,dc=com","password":"..."}`.
3. Observe that `escapedEmail` remains `attacker@example.com,ou=admins,dc=example,dc=com` (comma untouched by `EscapeFilter`), and the resulting `searchBaseDN` passed to `conn.Bind` is:
   `uid=attacker@example.com,ou=admins,dc=example,dc=com,ou=users,dc=example,dc=com`
   — an RDN structure different from the intended `uid=<email>,ou=users,dc=example,dc=com`, demonstrating that client input controls DN structure rather than only the attribute value. [4](#0-3) [5](#0-4)

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

**File:** core/web/sessions_controller_test.go (L44-53)
```go
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()

			ctx := t.Context()
			body := fmt.Sprintf(`{"email":"%s","password":"%s"}`, test.email, test.password)
			request, err := http.NewRequestWithContext(ctx, http.MethodPost, app.Server.URL+"/sessions", bytes.NewBufferString(body))
			require.NoError(t, err)
			resp, err := client.Do(request)
			require.NoError(t, err)
```
