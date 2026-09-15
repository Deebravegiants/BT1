The `go-ldap/ldap` vendor source isn't present in the index, but this is well-established public library behavior: `ldap.EscapeFilter` implements RFC 4515 filter escaping (backslash, `*`, `(`, `)`, NUL), not RFC 4514 DN escaping (comma, plus, quote, `<`, `>`, `;`, leading `#`/space). The relevant chainlink code confirms this mismatch is real and reachable from unauthenticated input.

### Title
LDAP Distinguished Name (DN) Injection via Filter-Only Escaping of User-Controlled Email in Login Bind - (File: core/sessions/ldapauth/ldap.go)

### Summary
`ldapAuthenticator.CreateSession` and `ldapAuthenticator.TestPassword` build the LDAP bind DN by escaping the unauthenticated, user-supplied `email` field with `ldap.EscapeFilter`, then splicing it directly into a DN string with `fmt.Sprintf`. `EscapeFilter` only escapes characters required for LDAP *search filter* safety (`\`, `*`, `(`, `)`, NUL) per RFC 4515; it does not escape DN metacharacters required by RFC 4514 (`,`, `+`, `"`, `<`, `>`, `;`, leading `#`/space, trailing space). This is the same root-cause class as the reported python-ldap advisory: an escaping helper applied in the wrong syntactic context, producing output that is not safe for its actual destination grammar (CWE-116).

### Finding Description
In `core/sessions/ldapauth/ldap.go`, `CreateSession` computes: [1](#0-0) 
and `TestPassword` does the same thing: [2](#0-1) 

`escapedEmail` is produced with `ldap.EscapeFilter`, a function whose contract is to escape values destined for an LDAP *search filter* string, not a DN. The resulting string is then concatenated with `fmt.Sprintf("%s=%s,%s,%s", ...)` directly into `searchBaseDN`, which is passed as the literal bind DN to `conn.Bind(...)`. Because DN-reserved characters (most importantly the comma `,` that separates RDNs) are not escaped by `EscapeFilter`, a value containing a comma is not neutralized before being embedded in the DN structure — it is interpreted as introducing additional RDN components rather than as a literal value of the leaf RDN.

`sr.Email` in `CreateSession` originates from the unauthenticated `sessions.SessionRequest` (the login request body), i.e., attacker-controlled input from an unprivileged actor hitting the login endpoint, before any credential has been validated.

### Impact Explanation
An attacker who controls the `email` field of a login request can inject additional DN components into the DN used for `conn.Bind`, altering which DN the server attempts to authenticate as. Combined with a password the attacker knows or controls (e.g., for an account they legitimately have, or through directory quirks such as case-insensitive/alias matching), this enables bind-target manipulation distinct from the intended `uid=<email>,<UsersDN>,<BaseDN>` structure — a form of authentication/identity confusion at the LDAP layer that undermines the guarantee that only the exact email-derived DN can be targeted. At minimum, it reliably causes malformed/failed LDAP requests before reaching intended validation logic (denial of service against the login path), and in directories with permissive relative/alternate DN resolution it broadens the DN surface an attacker can attempt to bind against.

### Likelihood Explanation
The vulnerable path is directly reachable by any unauthenticated caller of the login endpoint (`CreateSession`) and the password-test path (`TestPassword`), requiring no privileges — only supplying an `email` value containing DN metacharacters such as `,`. No special access or prior authentication is required to trigger the incorrect escaping.

### Recommendation
Use a proper DN-escaping function (RFC 4514) — e.g., a `ldap.EscapeDN`/manual RFC-4514 escaper — when constructing `searchBaseDN` values from user input, instead of `ldap.EscapeFilter`, which is only valid for values embedded inside filter expressions (as is correctly done in `FindUser`'s `filterQuery`, but not for the DN construction in `CreateSession`/`TestPassword`/`validateUsersActive`'s `searchBaseDN` composition pattern). Reject or reject-and-log any email containing RFC 4514 reserved DN characters before using it to build a bind DN, or use an LDAP library API that composes DN components structurally rather than via string formatting.

### Proof of Concept
1. Send a login request (`CreateSession`) with `sr.Email` set to a value containing a comma and additional RDN-like content, e.g. `attacker,ou=admins,dc=example,dc=com`.
2. `escapedEmail := ldap.EscapeFilter(...)` leaves the comma unescaped (it is not a filter metacharacter).
3. `searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())` produces a DN whose RDN sequence is altered by the injected comma-separated components rather than treating the whole value as a single RDN value.
4. `conn.Bind(searchBaseDN, sr.Password)` is issued against this attacker-influenced DN structure instead of the intended `uid=<email>,<UsersDN>,<BaseDN>`. [3](#0-2) [4](#0-3)

### Citations

**File:** core/sessions/ldapauth/ldap.go (L396-411)
```go
func (l *ldapAuthenticator) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		return "", errors.New("unable to establish connection to LDAP server with provided URL and credentials")
	}
	defer conn.Close()

	var returnErr error

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L503-514)
```go
// TestPassword tests if an LDAP login bind can be performed with provided credentials, returns nil if success
func (l *ldapAuthenticator) TestPassword(ctx context.Context, email string, password string) error {
	conn, err := l.ldapClient.CreateEphemeralConnection()
	if err != nil {
		return errors.New("unable to establish connection to LDAP server with provided URL and credentials")
	}
	defer conn.Close()

	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
```
