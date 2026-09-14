### Title
Enabling WebAuthn (2FA/MFA) does not revoke existing user sessions - (File: core/web/webauthn_controller.go)

### Summary
When a user enrolls a WebAuthn/MFA credential via `WebAuthnController.FinishRegistration`, the server saves the new credential and audits the event, but never invalidates the user's other active sessions. This mirrors CVE-2020-13307/BIT-gitlab-2020-13307, where GitLab failed to revoke existing sessions upon 2FA activation, allowing an attacker holding a previously stolen/hijacked session cookie to remain authenticated even after the legitimate user enables MFA as a remediation step.

### Finding Description
`FinishRegistration` completes MFA enrollment for the authenticated user and persists the credential: [1](#0-0) 

It calls `sessions.AddCredentialToUser` (which wraps `AuthenticationProvider.SaveWebAuthn`) and then audits `Auth2FAEnrolled`, but at no point does it call `ClearNonCurrentSessions` for the user's session ID, unlike the password-change flow which explicitly does so: [2](#0-1) [3](#0-2) 

The `ClearNonCurrentSessions` capability exists on the `AuthenticationProvider` interface and is implemented for local auth (`DELETE FROM sessions WHERE lower(email) = lower($1) AND id != $2`), so it is readily available but simply not invoked from the MFA enrollment path: [4](#0-3) [5](#0-4) 

The session-creation flow (`SessionsController.Create`) only requires WebAuthn if the user already has enrolled tokens at the time of login; it never re-validates sessions created before MFA was enabled: [6](#0-5) 

As a result, if an attacker has previously obtained a valid session cookie for the victim's account (e.g., via a leaked cookie, an unattended browser, or any other means of hijacking a `sessions` row keyed by `id`), that session remains valid in the `sessions` table after the victim proactively enrolls a hardware/WebAuthn key intending to lock out unauthorized access. The stale hijacked session bypasses the newly added MFA requirement entirely, because `AuthorizedUserWithSession` only checks session validity/expiry, not whether MFA was enabled after session creation: [7](#0-6) 

### Impact Explanation
This weakens the security guarantee that enrolling MFA "locks out" any other party who may hold a stolen session. An attacker with a hijacked but still-valid Chainlink node session cookie retains full API access (subject to the victim's role) indefinitely (until natural session expiry/timeout), even after the victim believes they've secured their account by adding a hardware key. Given the admin/edit/run privileges available through the node's web/API surface, this can lead to unauthorized configuration changes, key/job management, or fund-moving actions depending on the victim's role.

### Likelihood Explanation
Requires the attacker to already possess a valid (unexpired) session ID for the victim account, so it does not create the initial compromise—but it eliminates the self-remediation value of enabling MFA, which is exactly the abuse scenario described in the source advisory. This is a realistic post-compromise persistence scenario for a Chainlink operator UI (e.g., session token exposed via XSS, shared browser, or leaked logs) and requires no additional privilege from the unprivileged/attacker perspective once the session is obtained.

### Recommendation
Call `AuthenticationProvider().ClearNonCurrentSessions(ctx, sessionID)` in `WebAuthnController.FinishRegistration` after successfully saving the new WebAuthn credential, mirroring the pattern already used in `UserController.updateUserPassword` and the `UpdateUserPassword` GraphQL resolver, so that enabling 2FA invalidates all other outstanding sessions for that user.

### Proof of Concept
1. Attacker obtains victim's valid session cookie/ID (e.g., via XSS, shared device, or log leakage) and keeps making authenticated requests.
2. Victim logs in normally and enrolls a WebAuthn key via `GET /v2/enroll_webauthn` then `POST /v2/enroll_webauthn` (`WebAuthnController.BeginRegistration` / `FinishRegistration`), successfully completing MFA setup and receiving `Auth2FAEnrolled` audit confirmation.
3. Attacker's previously captured session cookie is still present in the `sessions` table (not deleted by step 2) and remains usable against any `/v2/*` authenticated endpoint until it naturally expires, completely bypassing the newly enabled MFA requirement.

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

**File:** core/web/resolver/mutation.go (L959-967)
```go
	if err = r.App.AuthenticationProvider().ClearNonCurrentSessions(ctx, session.SessionID); err != nil {
		return nil, clearSessionsError{}
	}

	err = r.App.AuthenticationProvider().SetPassword(ctx, &dbUser, args.Input.NewPassword)
	if err != nil {
		return nil, failedPasswordUpdateError{}
	}

```

**File:** core/sessions/localauth/orm.go (L83-107)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired, and update session's LastUsed field.
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired, and update session's LastUsed field.
func (o *orm) AuthorizedUserWithSession(ctx context.Context, sessionID string) (user sessions.User, err error) {
	if len(sessionID) == 0 {
		return sessions.User{}, sessions.ErrEmptySessionID
	}

	email, err := o.findValidSession(ctx, sessionID)
	if err != nil {
		return sessions.User{}, sessions.ErrUserSessionExpired
	}

	user, err = o.findUser(ctx, email)
	if err != nil {
		return sessions.User{}, sessions.ErrUserSessionExpired
	}

	if err := o.updateSessionLastUsed(ctx, sessionID); err != nil {
		return sessions.User{}, err
	}

	return user, nil
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

**File:** core/sessions/authentication.go (L43-64)
```go
// AuthenticationProvider is an interface that abstracts the required application calls to a user management backend
// Currently localauth (users table DB) or LDAP server (readonly)
type AuthenticationProvider interface {
	FindUser(ctx context.Context, email string) (User, error)
	FindUserByAPIToken(ctx context.Context, apiToken string) (User, error)
	ListUsers(ctx context.Context) ([]User, error)
	AuthorizedUserWithSession(ctx context.Context, sessionID string) (User, error)
	DeleteUser(ctx context.Context, email string) error
	DeleteUserSession(ctx context.Context, sessionID string) error
	CreateSession(ctx context.Context, sr SessionRequest) (string, error)
	ClearNonCurrentSessions(ctx context.Context, sessionID string) error
	CreateUser(ctx context.Context, user *User) error
	UpdateRole(ctx context.Context, email, newRole string) (User, error)
	SetAuthToken(ctx context.Context, user *User, token *auth.Token) error
	CreateAndSetAuthToken(ctx context.Context, user *User) (*auth.Token, error)
	DeleteAuthToken(ctx context.Context, user *User) error
	SetPassword(ctx context.Context, user *User, newPassword string) error
	TestPassword(ctx context.Context, email, password string) error
	Sessions(ctx context.Context, offset, limit int) ([]Session, error)
	GetUserWebAuthn(ctx context.Context, email string) ([]WebAuthn, error)
	SaveWebAuthn(ctx context.Context, token *WebAuthn) error
	ExtendRouter(r *gin.RouterGroup) error
```

**File:** core/web/sessions_controller.go (L29-60)
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
