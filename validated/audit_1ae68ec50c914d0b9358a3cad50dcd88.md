## Analog Vulnerability Found

### Title
Local WebAuthn MFA is never enforced for the local-admin login fallback when OIDC/SSO authentication is enabled - (File: `core/sessions/oidcauth/oidc.go`)

### Summary
When the Chainlink node is configured to use the OIDC/SSO authenticator, the `oidcAuthenticator` implementation of `AuthenticationProvider` replaces `localauth.orm` as the active `AuthenticationProvider` for the node (`core/services/chainlink/application.go` calls `NewOIDCAuthenticator`). This authenticator still exposes a local-admin login path (`CreateSession` → `localLoginFallback`) against the same shared `users` table, but it never checks or enforces WebAuthn MFA that a user may have enrolled, because `GetUserWebAuthn` is hard-coded to return an empty list.

### Finding Description
In the standard local-auth flow (`core/sessions/localauth/orm.go`), `CreateSession` fetches the user's enrolled WebAuthn credentials via `GetUserWebAuthn` and requires a valid WebAuthn attestation before issuing a session if any credentials are registered: [1](#0-0) 

However, `oidcAuthenticator` (used when SSO/OIDC is the active authentication provider) implements `GetUserWebAuthn` as a stub that unconditionally returns an empty credential list, with a comment claiming "MFA is delegated to SAML provider": [2](#0-1) 

Its `CreateSession` method delegates only to `localLoginFallback`, which checks email and password against the same shared `users` table used by local auth, but performs no MFA/WebAuthn check whatsoever before minting a session: [3](#0-2) [4](#0-3) 

Because `users` and `web_authns` are shared tables (the same schema used by `localauth.orm.GetUserWebAuthn`, `core/sessions/localauth/orm.go:130-139`), an admin account that has locally enrolled a WebAuthn/MFA credential retains that enrollment in the database regardless of which `AuthenticationProvider` is active. If the node is switched to (or deployed with) the OIDC authenticator, that same account's local-admin login path (`/sessions` login endpoint backed by `CreateSession`) succeeds with password alone — the enrolled second factor is silently never checked. This exactly mirrors the reported bug class: "does not enforce locally configured MFA during SSO authentication, allowing users to bypass second-factor requirements."

### Impact Explanation
An attacker who obtains or brute-forces only the password of an admin/edit-role account that has WebAuthn MFA enrolled can fully authenticate and obtain a valid session/role (up to `UserRoleAdmin`) on any Chainlink node running with the OIDC authenticator enabled, completely bypassing the second factor the operator believed was protecting that account. This grants full administrative access to node management APIs (job management, keys, bridges, etc.), a critical authentication bypass.

### Likelihood Explanation
Any deployment that enables OIDC/SSO (`core/config` `OIDC` settings) while still supporting the documented local-admin fallback login is affected — this is presented as a normal supported feature ("a separate `/oidc-login` route is defined... to initiate the SAML/OIDC flow", implying the default `/sessions` route with `localLoginFallback` remains the local-admin path). No special privilege is required to exploit; only knowledge of the local admin's password is needed, which is exactly the credential MFA is meant to protect against.

### Recommendation
In `oidcAuthenticator.CreateSession` / `localLoginFallback`, query and enforce the shared `web_authns` table (the same logic used in `localauth.orm.CreateSession`) before issuing a session for the local-admin fallback path, instead of stubbing `GetUserWebAuthn` to always return empty. If MFA truly cannot be delegated to the OIDC provider in this fallback path, the local-admin fallback login should be disabled entirely when OIDC is active, or require WebAuthn verification identical to the local-auth flow.

### Proof of Concept
1. Configure a Chainlink node with OIDC/SSO authentication enabled so `oidcAuthenticator` becomes the active `AuthenticationProvider`.
2. Ensure the local admin user (row in the `users` table) has previously enrolled a WebAuthn/MFA credential (row in `web_authns`), e.g. from before OIDC was enabled or enrolled while it briefly used local auth.
3. Send a login request with only the correct `email`/`password` to the standard session-creation endpoint (`POST /sessions`), omitting `WebAuthnData`.
4. Observe that `oidcAuthenticator.CreateSession` → `localLoginFallback` returns a valid session immediately, with no WebAuthn challenge ever issued, unlike `localauth.orm.CreateSession` which would return an HTTP 401/challenge requiring the hardware key (`core/sessions/localauth/orm.go:181-199`).

### Citations

**File:** core/sessions/localauth/orm.go (L164-199)
```go
	// Load all valid MFA tokens associated with user's email
	uwas, err := o.GetUserWebAuthn(ctx, user.Email)
	if err != nil {
		// There was an error with the database query
		lggr.Errorf("Could not fetch user's MFA data: %v", err)
		return "", pkgerrors.New("MFA Error")
	}

	// No webauthn tokens registered for the current user, so normal authentication is now complete
	if len(uwas) == 0 {
		lggr.Infof("No MFA for user. Creating Session")
		session := sessions.NewSession()
		_, err = o.ds.ExecContext(ctx, "INSERT INTO sessions (id, email, last_used, created_at) VALUES ($1, $2, now(), now())", session.ID, user.Email)
		o.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})
		return session.ID, err
	}

	// Next check if this session request includes the required WebAuthn challenge data
	// if not, return a 401 error for the frontend to prompt the user to provide this
	// data in the next round trip request (tap key to include webauthn data on the login page)
	if sr.WebAuthnData == "" {
		lggr.Warnf("Attempted login to MFA user. Generating challenge for user.")
		options, webauthnError := sessions.BeginWebAuthnLogin(user, uwas, sr)
		if webauthnError != nil {
			lggr.Errorf("Could not begin WebAuthn verification: %v", webauthnError)
			return "", pkgerrors.New("MFA Error")
		}

		j, jsonError := json.Marshal(options)
		if jsonError != nil {
			lggr.Errorf("Could not serialize WebAuthn challenge: %v", jsonError)
			return "", pkgerrors.New("MFA Error")
		}

		return "", pkgerrors.New(string(j))
	}
```

**File:** core/sessions/oidcauth/oidc.go (L404-407)
```go
// GetUserWebAuthn returns an empty stub, MFA is delegated to SAML provider
func (oi *oidcAuthenticator) GetUserWebAuthn(ctx context.Context, email string) ([]clsessions.WebAuthn, error) {
	return []clsessions.WebAuthn{}, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L409-439)
```go
// CreateSession in the context of the OIDC driver handles only the local auth admin user, exposed by the default endpoint defined in the router. To initiate the SAML/OIDC
// flow, a separate /oidc-login route is defined which handles the redirect to the
// configured provider
func (oi *oidcAuthenticator) CreateSession(ctx context.Context, sr clsessions.SessionRequest) (string, error) {
	foundUser, err := oi.localLoginFallback(ctx, sr)
	if err != nil {
		return "", err
	}

	sanitizedEmail := strings.ReplaceAll(sr.Email, "\n", "")
	sanitizedEmail = strings.ReplaceAll(sanitizedEmail, "\r", "")
	oi.lggr.Infof("Successful local admin login request for user %s - %s", sanitizedEmail, foundUser.Role)

	// Save local admin session, user, and role to sessions table
	// Sessions are set to expire after the duration + creation date elapsed
	session := clsessions.NewSession()
	_, err = oi.ds.ExecContext(ctx,
		"INSERT INTO oidc_sessions (id, user_email, user_role, created_at) VALUES ($1, $2, $3, now())",
		session.ID,
		strings.ToLower(sr.Email),
		foundUser.Role,
	)
	if err != nil {
		oi.lggr.Errorf("unable to create new session in oidc_sessions table %v", err)
		return "", fmt.Errorf("error creating local OIDC session: %w", err)
	}

	oi.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})

	return session.ID, nil
}
```

**File:** core/sessions/oidcauth/oidc.go (L578-597)
```go
// localLoginFallback tests the credentials provided against the 'local' authentication method
// This covers the case of local CLI API calls requiring local login separate from the OIDC server
func (oi *oidcAuthenticator) localLoginFallback(ctx context.Context, sr clsessions.SessionRequest) (clsessions.User, error) {
	var user clsessions.User
	err := oi.ds.GetContext(ctx, &user, SQLSelectUserbyEmail, sr.Email)
	if err != nil {
		return user, err
	}
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return user, errors.New("invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		oi.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return user, errors.New("invalid password")
	}

	return user, nil
}
```
