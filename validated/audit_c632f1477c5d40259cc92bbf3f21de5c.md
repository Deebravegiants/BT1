This confirms the analog exists. `ClearNonCurrentSessions` is called only when changing a password (`core/web/user_controller.go:341-360`, `core/web/resolver/mutation.go:934-970`), but is never invoked in `WebAuthnController.FinishRegistration` (`core/web/webauthn_controller.go:62-104`) when a user newly enrolls a 2FA/WebAuthn credential. This is the same bug class as the Cal.com CVE-2023-37919: enabling 2FA does not invalidate other active sessions, so a session hijacked or left open on another device before 2FA enrollment remains valid indefinitely and bypasses the newly added MFA requirement entirely.

### Title
Enabling WebAuthn (2FA) does not invalidate other active sessions - (File: core/web/webauthn_controller.go)

### Summary
When a Chainlink node user enrolls a new WebAuthn/2FA credential via `FinishRegistration`, the handler saves the credential and emits an audit event but never calls `ClearNonCurrentSessions` to terminate other active sessions tied to that user's email.

### Finding Description
`FinishRegistration` in [1](#0-0)  validates the WebAuthn attestation, persists the credential with `sessions.AddCredentialToUser`, and audits `Auth2FAEnrolled`, but performs no session-store cleanup. Compare this to the password-change flow, which explicitly clears all other sessions before rotating the password: `orm.ClearNonCurrentSessions(ctx, sessionID)` followed by `orm.SetPassword(...)` in [2](#0-1) , and the identical pattern in the GraphQL resolver `UpdateUserPassword` at [3](#0-2) . The `AuthenticationProvider` interface exposes `ClearNonCurrentSessions(ctx, sessionID)` precisely for this purpose ( [4](#0-3) ), and it is implemented across all three auth backends — local ( [5](#0-4) ), LDAP, and OIDC ( [6](#0-5) ) — but `WebAuthnController.FinishRegistration` never invokes it.

Because `sessions` table rows are keyed only by session ID and email (not tied to whether 2FA was required at creation time), any session created via `SessionsController.Create` before 2FA enrollment — for `CreateSession` in the no-MFA branch of [7](#0-6)  — remains valid after 2FA is turned on for that account. `AuthorizedUserWithSession` does not re-check whether the account now requires 2FA; it simply looks up the still-present session row.

### Impact Explanation
If an attacker (or a previously logged-in device the legitimate user no longer trusts) already holds a valid session cookie for a Chainlink Operator UI account, enrolling a hardware security key on that account does not revoke the attacker's session. The attacker retains full access to the node's admin UI/API (job management, keys, bridges, chains, external initiators) exactly as before, defeating the purpose of adding 2FA as a compromise-recovery or hardening measure. This aligns with the "unauthorized job run or fund movement" and "authentication bypass" categories, since the Operator UI session grants privileged node administration capability.

### Likelihood Explanation
Exploitation requires only that a session already exists for the account (e.g., stolen cookie, unattended browser, shared device) at the time 2FA is enabled — no additional privilege or interaction with the 2FA setup itself is needed by the attacker. This is a realistic scenario: enabling 2FA is a common response to suspected credential compromise, which is precisely the case this flaw fails to protect against.

### Recommendation
In `WebAuthnController.FinishRegistration`, after successfully calling `sessions.AddCredentialToUser`, obtain the current session ID (as done via `getCurrentSessionID` in [8](#0-7) ) and call `orm.ClearNonCurrentSessions(ctx, sessionID)` before returning success, mirroring the password-change flow.

### Proof of Concept
1. Log in to the Chainlink Operator UI on Device A and Device B with the same account (no 2FA yet), obtaining two valid session cookies via `SessionsController.Create`.
2. On Device A, register a WebAuthn/2FA key by calling `POST /webauthn/begin` then `POST /webauthn/finish` (`WebAuthnController.BeginRegistration` / `FinishRegistration`).
3. On Device B, continue issuing authenticated requests (e.g., `GET /v2/user` or any admin endpoint) using the original session cookie.
4. Observe that Device B's session is still accepted by `AuthorizedUserWithSession`, despite 2FA now being enabled on the account — no re-authentication or 2FA challenge is required for the pre-existing session.

### Citations

**File:** core/web/webauthn_controller.go (L62-103)
```go
func (w *WebAuthnController) FinishRegistration(c *gin.Context) {
	ctx := c.Request.Context()
	user, ok := auth.GetAuthenticatedUser(c)
	if !ok {
		logger.Sugared(w.App.GetLogger()).AssumptionViolationf("failed to obtain current user from context")
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to register key"))
		return
	}

	orm := w.App.AuthenticationProvider()
	uwas, err := orm.GetUserWebAuthn(ctx, user.Email)
	if err != nil {
		w.App.GetLogger().Errorf("failed to obtain current user MFA tokens: error in GetUserWebAuthn: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to register key"))
		return
	}

	webAuthnConfig := w.App.GetWebAuthnConfiguration()

	credential, err := w.inProgressRegistrationsStore.FinishWebAuthnRegistration(*user, uwas, c.Request, webAuthnConfig)
	if err != nil {
		w.App.GetLogger().Errorf("error in FinishWebAuthnRegistration: %s", err)
		jsonAPIError(c, http.StatusBadRequest, errors.New("registration was unsuccessful"))
		return
	}

	if sessions.AddCredentialToUser(ctx, w.App.AuthenticationProvider(), user.Email, credential) != nil {
		w.App.GetLogger().Errorf("Could not save WebAuthn credential to DB for user: %s", user.Email)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}

	// Forward registered credentials for audit logs
	credj, err := json.Marshal(credential)
	if err != nil {
		w.App.GetLogger().Errorf("error in Marshal credentials: %s", err)
		jsonAPIError(c, http.StatusBadRequest, errors.New("registration was unsuccessful"))
		return
	}
	w.App.GetAuditLogger().Audit(audit.Auth2FAEnrolled, map[string]any{"email": user.Email, "credential": string(credj)})

	c.String(http.StatusOK, "{}")
```

**File:** core/web/user_controller.go (L332-339)
```go
func getCurrentSessionID(c *gin.Context) (string, error) {
	session := sessions.Default(c)
	sessionID, ok := session.Get(webauth.SessionIDKey).(string)
	if !ok {
		return "", errors.New("unable to get current session ID")
	}
	return sessionID, nil
}
```

**File:** core/web/user_controller.go (L341-360)
```go
func (u *UserController) updateUserPassword(c *gin.Context, user *clsession.User, newPassword string) error {
	ctx := c.Request.Context()
	sessionID, err := getCurrentSessionID(c)
	if err != nil {
		return err
	}
	orm := u.App.AuthenticationProvider()
	if err := orm.ClearNonCurrentSessions(ctx, sessionID); err != nil {
		u.App.GetLogger().Errorf("failed to clear non current user sessions: %s", err)
		return errors.New("unable to update password")
	}
	if err := orm.SetPassword(ctx, user, newPassword); err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			return errUnsupportedForAuth
		}
		u.App.GetLogger().Errorf("failed to update current user password: %s", err)
		return errors.New("unable to update password")
	}
	return nil
}
```

**File:** core/web/resolver/mutation.go (L959-963)
```go
	if err = r.App.AuthenticationProvider().ClearNonCurrentSessions(ctx, session.SessionID); err != nil {
		return nil, clearSessionsError{}
	}

	err = r.App.AuthenticationProvider().SetPassword(ctx, &dbUser, args.Input.NewPassword)
```

**File:** core/sessions/authentication.go (L53-53)
```go
	ClearNonCurrentSessions(ctx context.Context, sessionID string) error
```

**File:** core/sessions/localauth/orm.go (L172-179)
```go
	// No webauthn tokens registered for the current user, so normal authentication is now complete
	if len(uwas) == 0 {
		lggr.Infof("No MFA for user. Creating Session")
		session := sessions.NewSession()
		_, err = o.ds.ExecContext(ctx, "INSERT INTO sessions (id, email, last_used, created_at) VALUES ($1, $2, now(), now())", session.ID, user.Email)
		o.auditLogger.Audit(audit.AuthLoginSuccessNo2FA, map[string]any{"email": sr.Email})
		return session.ID, err
	}
```

**File:** core/sessions/localauth/orm.go (L243-251)
```go
// ClearNonCurrentSessions removes other sessions for the user tied to sessionID.
func (o *orm) ClearNonCurrentSessions(ctx context.Context, sessionID string) error {
	var email string
	if err := o.ds.GetContext(ctx, &email, "SELECT email FROM sessions WHERE id = $1", sessionID); err != nil {
		return err
	}
	_, err := o.ds.ExecContext(ctx, "DELETE FROM sessions WHERE lower(email) = lower($1) AND id != $2", email, sessionID)
	return err
}
```

**File:** core/sessions/oidcauth/oidc.go (L441-449)
```go
// ClearNonCurrentSessions removes other oidc_sessions for the user tied to sessionID.
func (oi *oidcAuthenticator) ClearNonCurrentSessions(ctx context.Context, sessionID string) error {
	var email string
	if err := oi.ds.GetContext(ctx, &email, "SELECT user_email FROM oidc_sessions WHERE id = $1", sessionID); err != nil {
		return err
	}
	_, err := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE lower(user_email) = lower($1) AND id != $2", email, sessionID)
	return err
}
```
