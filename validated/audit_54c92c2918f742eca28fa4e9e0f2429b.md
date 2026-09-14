## Analysis

This CVE describes an authentication bypass where an LDAP-backed authentication system fails to validate credentials, letting an attacker who knows the bind DN pattern authenticate without a valid password. The chainlink node's LDAP authenticator has an analogous root cause: it forwards the client-supplied password directly into an LDAP simple bind with no check for an empty password string, which triggers RFC 4513 "unauthenticated bind" semantics on many LDAP servers (the bind succeeds without the server actually verifying any password).

### Title
LDAP authentication bypass via empty-password unauthenticated bind - (File: core/sessions/ldapauth/ldap.go)

### Summary
`ldapAuthenticator.CreateSession` builds a bind DN directly from client-supplied email and calls `conn.Bind(searchBaseDN, sr.Password)` without ever validating that `sr.Password` is non-empty. [1](#0-0)  The same missing check exists in `TestPassword`. [2](#0-1) 

### Finding Description
Per RFC 4513 §5.1.2, an LDAP simple bind request with a non-empty DN and a zero-length password is defined as an "unauthenticated bind." Many LDAP server implementations/configurations (misconfigured OpenLDAP, some AD setups, etc.) return success for such a bind because it is treated as an anonymous/unauthenticated operation rather than a credential check — the server never compares any password. `CreateSession` constructs the DN purely from the attacker-controlled `sr.Email` field (`l.config.BaseUserAttr() + "=" + escapedEmail + "," + l.config.UsersDN() + "," + l.config.BaseDN()`) and passes `sr.Password` straight into `conn.Bind`, with `err == nil` treated as full authentication success — no additional secret-comparison step is performed. [3](#0-2)  This mirrors CVE-2014-3999's bug class: the authenticator trusts the underlying LDAP bind's success/failure to *be* the authentication decision, without accounting for LDAP semantics that decouple "bind succeeded" from "credentials were verified" (unauthenticated/anonymous binds), so an attacker with mere knowledge of a valid user's email (the "bind user DN" component) can bypass authentication by supplying an empty password.

The client-facing entrypoint is unauthenticated by design (it's the login endpoint): `SessionsController.Create` binds the raw JSON body to `SessionRequest` and forwards it straight to `AuthenticationProvider().CreateSession`. [4](#0-3)  There is no server-side rejection of an empty `password` field before it reaches the LDAP bind call.

### Impact Explanation
If the deployed LDAP server (or any misconfigured directory in the operator's environment) honors unauthenticated binds, any unprivileged network client that knows or can guess a valid user's email address can obtain a valid Chainlink node session with that user's role (Admin/Edit/Run/View) without any password. Because `FindUser`/group lookups determine the session's role afterward, this can yield full administrative access to the node's API, cookie-based UI session, and (if the account has one) subsequent access to sensitive job/fund-moving operations.

### Likelihood Explanation
Exploitability depends on whether the operator's LDAP server is configured to allow unauthenticated binds (many are not, by default, per RFC 4513 recommendations, but misconfiguration for this exact class of bug is common and is precisely the CVE-2014-3999 bug class). The chainlink code itself performs no defense-in-depth check to reject an empty password before delegating to the LDAP server, so the chainlink node offers no mitigation if the upstream directory is misconfigured.

### Recommendation
Reject `SessionRequest.Password == ""` (and `TestPassword`'s `password == ""`) before calling `conn.Bind`, returning an authentication failure immediately, so that unauthenticated/anonymous LDAP binds can never be interpreted as successful credential validation. Add explicit unit tests asserting empty-password login attempts are rejected regardless of what the mocked LDAP connection returns for `Bind`.

### Proof of Concept
1. Obtain (or guess) a valid LDAP user email configured in `UsersDN`, e.g. `victim@example.com`.
2. `POST /sessions` with body `{"email":"victim@example.com","password":""}`.
3. `SessionsController.Create` forwards this to `ldapAuthenticator.CreateSession`, which calls `conn.Bind("uid=victim@example.com,...", "")`. [5](#0-4) 
4. If the upstream LDAP server treats this as an unauthenticated bind and returns `nil` error, `CreateSession` proceeds to look up the user's role and issues a valid session cookie for `victim@example.com` — without ever knowing their password.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L405-416)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}

	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
```

**File:** core/sessions/ldapauth/ldap.go (L511-517)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
	if err == nil {
		return nil
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
