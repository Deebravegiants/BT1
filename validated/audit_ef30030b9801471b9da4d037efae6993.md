Nothing in SECURITY.md excludes this class of finding, and the code confirms the claim precisely: both `CreateSession` and `TestPassword` build a Bind DN with `ldap.EscapeFilter` (which only escapes `*`, `(`, `)`, `\`, NUL for search filters) instead of proper DN escaping, then splice the unauthenticated caller's `Email`/`email` field directly into a DN string passed to `conn.Bind()`.

Audit Report

## Title
LDAP DN Injection in CreateSession/TestPassword Bind via Filter-Escaped (Not DN-Escaped) Email - ([File: core/sessions/ldapauth/ldap.go])

## Summary
`CreateSession` and `TestPassword` in `core/sessions/ldapauth/ldap.go` build the LDAP Bind DN by concatenating the caller-supplied `email`/`sr.Email` into a DN string sanitized only with `ldap.EscapeFilter`, which escapes filter metacharacters (`*`, `(`, `)`, `\`, NUL) but not DN metacharacters (`,`, `+`, `"`, `<`, `>`, `;`, leading `#`/space). Because these functions are reachable by an unauthenticated login request, an attacker can inject unescaped commas into the constructed DN passed to `conn.Bind()`, altering its RDN structure.

## Finding Description
`CreateSession` (invoked from the unauthenticated Session login API) computes: [1](#0-0) 
and `TestPassword` (used for local admin/API credential verification) performs the identical construction: [2](#0-1) 

Both use `fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())` where `escapedEmail` is produced only via `ldap.EscapeFilter(strings.ToLower(...))`. That function is designed for values embedded in `(attr=value)` search filters, not DN RDN components, and does not escape commas or other DN separators. The resulting string is used directly as the DN argument to `conn.Bind(searchBaseDN, sr.Password)` / `conn.Bind(searchBaseDN, password)`, so an attacker-controlled `Email` value with an unescaped comma can append or alter RDN components in the DN being bound. Contrast this with `FindUser`, which uses `escapedEmail` correctly inside a `filterQuery` for a `Search` operation, not for a raw Bind DN — the misuse is specific to `CreateSession` and `TestPassword`.

No authentication middleware sits in front of `CreateSession`; it's the login handler itself, so the malformed-escaping code path is reachable pre-authentication, and `TestPassword`'s local-fallback credential check does not validate DN structure either.

## Impact Explanation
This maps to the in-scope "node API authentication or role bypass" impact category: if the manipulated Bind DN can be coerced by an unauthenticated attacker into successfully binding as (or probing for) an unintended directory entry, it could lead to unauthorized session issuance (`sessions.NewSession()` → `INSERT INTO ldap_sessions`) and role assignment. The severity is bounded by how permissive the specific upstream LDAP server is to malformed/injected DNs during `Bind` — this is an objectively wrong escaping function for the DN sink, matching the CWE-90 LDAP injection root cause pattern.

## Likelihood Explanation
`CreateSession` is reachable by any unauthenticated client submitting `Email`/`Password` to the login endpoint, requiring no prior credential or role. `TestPassword` is invoked in the credential-verification code path with the same flawed escaping. The vulnerability is deterministic in that the sanitizer is provably the wrong one for the sink (comma passes through untouched), though actual exploitation to achieve a bind/auth bypass depends on the configured LDAP server's DN parsing/tolerance — this is a property of the target infrastructure, not of this code, and no PoC against a real/representative LDAP server backing this repo was demonstrated to show a concrete authentication bypass or data disclosure resulting from the injected DN.

## Recommendation
- Replace `ldap.EscapeFilter` with a proper RFC 4514 DN-escaping function (e.g. `ldap.EscapeDN` if available in the go-ldap version in use) for values placed into DN strings in `CreateSession` (lines 406–407) and `TestPassword` (lines 512–513).
- Alternatively, avoid building Bind DNs from user input: perform an `EscapeFilter`-based `Search` with the read-only service account to resolve the target user's real DN (as `FindUser` already does), then `Bind` using that resolved DN and the user-supplied password.
- Add regression tests supplying emails containing `,`, `+`, `"`, `<`, `>`, `;` to confirm the resulting DN is not structurally alterable.

## Proof of Concept
1. `POST` to the login endpoint mapping to `CreateSession` with `sr.Email` = `"attacker@example.com,ou=Admins,dc=example,dc=com"` and an attacker-chosen password.
2. `ldap.EscapeFilter` leaves the comma-delimited suffix unescaped since it only escapes `*()\`/NUL: [3](#0-2) 
3. Observe (via mocked `LDAPConn.Bind` in a unit test, following the pattern in `core/sessions/ldapauth/ldap_test.go` `TestORM_CreateSession_UpstreamBind`) that the DN string passed to `Bind` contains the injected RDN components, demonstrating the sanitizer fails to prevent structural DN alteration — a full end-to-end authentication-bypass demonstration would additionally require a representative upstream LDAP server to confirm exploitability of the altered Bind call.

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
