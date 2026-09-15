Audit Report

## Title
LDAP DN injection in `CreateSession`/`TestPassword` due to filter-escaping (not DN-escaping) of attacker-controlled email - (File: `core/sessions/ldapauth/ldap.go`)

## Summary
`CreateSession` and `TestPassword` in `core/sessions/ldapauth/ldap.go` sanitize the attacker-controlled email with `ldap.EscapeFilter` (RFC 4515 filter escaping) before splicing it into the LDAP bind DN string via `fmt.Sprintf`, rather than using an RFC 4514 DN-escaping routine. Since `EscapeFilter` does not escape DN metacharacters such as `,`, `+`, `"`, `<`, `>`, or `;`, a caller can alter the number and structure of RDN components in the DN that `conn.Bind()` ultimately authenticates against.

## Finding Description
`CreateSession` builds the bind DN as: [1](#0-0) 
using only `ldap.EscapeFilter`, which is confirmed by the imports and usage in the file to be the `go-ldap/v3` filter-escaping helper. The same pattern exists in the password-testing path around L511-514, and correctly contrasts with `FindUser`'s and `validateUsersActive`'s filter construction, where `EscapeFilter` is the *appropriate* choice because those values are placed inside a search filter, not a DN: [2](#0-1) 

This endpoint is reachable pre-auth via `POST /sessions`: [3](#0-2) 

No validation rejects DN metacharacters in `sr.Email` before it reaches `CreateSession`, and no DN-specific escaping (e.g., manual RFC 4514 escaping) is applied anywhere in this file. This confirms the code behaves exactly as described: a comma in the email field is not neutralized and changes the DN structure passed to `conn.Bind()`.

## Impact Explanation
The security assumption broken is that the bind target is always `uid=<single-RDN-value>,<UsersDN>,<BaseDN>`. In practice an unauthenticated caller can append additional RDN components ahead of the intended `UsersDN`/`BaseDN` suffix. However, actually leveraging this to authenticate as an unintended identity still requires the attacker to supply a password that is valid for whatever resulting DN is formed — the bug does not by itself allow binding without correct credentials for the resolved target entry. This bounds the practical impact to: (a) directory-structure/probing information leakage via bind-error timing/content differences, and (b) a directory-dependent path to reach unintended entries if such an entry happens to exist and the caller separately knows valid credentials for it. This is a real violation of DN-construction hygiene and a legitimate secondary-defense gap, but it does not on its own demonstrate an authentication bypass, since LDAP bind still requires a correct password for whatever DN results, and common LDAP client libraries (including `go-ldap`) additionally guard against the classic unauthenticated/anonymous-bind bypass by rejecting empty passwords by default.

## Likelihood Explanation
Any unauthenticated actor can send arbitrary `email` values to `POST /sessions`, so the injection itself is trivially reachable with no privileges. Turning the DN-structure manipulation into an actual authentication bypass or account takeover requires directory-specific conditions (a reachable unintended DN and knowledge of valid credentials for it) that are not demonstrated in the PoC — the PoC only shows that the resulting DN string changes, not that authentication succeeds against an unintended identity without correct credentials.

## Recommendation
Replace `ldap.EscapeFilter` with a proper RFC 4514 DN-escaping routine (e.g., `ldap.EscapeDN` in newer `go-ldap` versions, or manual escaping of `,`, `+`, `"`, `<`, `>`, `;`, `=`, leading `#`/space, and trailing space) at every site where a user-supplied value is concatenated into a bind DN or search base DN in `core/sessions/ldapauth/ldap.go` (`CreateSession`, `TestPassword`, and the analogous helper around L511-514) and in `core/sessions/ldapauth/client.go` if applicable. Reserve `EscapeFilter` exclusively for values embedded in LDAP search filter expressions. As defense in depth, reject email values containing DN metacharacters before they are used in any DN-construction context.

## Proof of Concept
1. Configure `WebServer.AuthenticationMethod = 'ldap'` with `BaseUserAttr = 'uid'`, `UsersDN = 'ou=users'`, `BaseDN = 'dc=example,dc=com'`.
2. Send an unauthenticated `POST /sessions` request with `{"email": "victim,ou=someOtherOU,dc=example,dc=com", "password": "<guess>"}`.
3. Observe that `CreateSession` constructs `searchBaseDN = "uid=victim,ou=someOtherOU,dc=example,dc=com,ou=users,dc=example,dc=com"` instead of `uid=victim,ou=users,dc=example,dc=com`, confirming the comma is not neutralized before being placed in the DN passed to `conn.Bind()`. Note that a full authentication-bypass demonstration additionally requires a directory layout where the crafted DN resolves to a real entry and a correct password for that entry — this was not demonstrated and remains directory-dependent.

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
