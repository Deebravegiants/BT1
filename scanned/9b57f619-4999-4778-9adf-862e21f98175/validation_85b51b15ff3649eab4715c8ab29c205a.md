Based on my investigation, I found a valid analog in the chainlink node's WebAuthn/MFA enrollment endpoints.

### Title
Missing server-side password re-authentication when enrolling a new WebAuthn (2FA) credential - (File: core/web/webauthn_controller.go)

### Summary
The chainlink node exposes `WebAuthnController.BeginRegistration` and `WebAuthnController.FinishRegistration`, which let an already-authenticated user enroll a new MFA/WebAuthn credential on their account. Unlike other sensitive account-security mutations in the same package (password change, API-token deletion), these handlers perform **no password re-verification** — they only check that a valid session/token exists.

### Finding Description
`FinishRegistration` (and `BeginRegistration`) only call `auth.GetAuthenticatedUser(c)` to fetch the user from context and then proceed directly to `FinishWebAuthnRegistration` / `AddCredentialToUser`, persisting a brand-new WebAuthn credential tied to the account: [1](#0-0) 

Compare this to the two other sensitive, "prove you're really the account owner" actions in the same package, `UserController.UpdatePassword` and `UserController.DeleteAPIToken`, which explicitly re-check the password/hash before proceeding: [2](#0-1) [3](#0-2) 

This inconsistency mirrors the CVE-2025-32359 bug class: a security-sensitive 2FA-configuration change is only guarded by a valid session, with no explicit server-side re-authentication step, so if such re-auth exists only in the Operator UI frontend flow, it can be trivially bypassed by calling the REST endpoints directly.

### Impact Explanation
Any party in possession of a valid session cookie or API token for a victim account (e.g., via XSS, a leaked/lingering token, or a hijacked browser session) can silently register their own WebAuthn key as a second factor on the victim's account — without knowing the victim's password — via `POST` to the WebAuthn registration endpoints. Because MFA/WebAuthn is meant to be a *second, independent* factor bound to knowledge of the current password, this bypass allows an attacker to persist a durable authentication factor on the account, which can be leveraged for continued access even after the original session/token is revoked or the password is rotated (since password rotation via `UpdatePassword` only calls `ClearNonCurrentSessions`, not `DeleteWebAuthn`/credential revocation): [4](#0-3) 

### Likelihood Explanation
Exploitation requires the attacker to already have a valid authenticated session or API token for the target account (e.g., via a stolen cookie, XSS, or token leak) — it is not exploitable by a fully anonymous actor. This matches the CVSS vector of the underlying CVE (`PR:N`/`UI:N` but `AC:H`), reflecting a real but constrained-likelihood bypass rather than a trivial unauthenticated compromise.

### Recommendation
Require re-verification of the current password (via `AuthenticationProvider.TestPassword`, as already used in `DeleteAPIToken`) as part of the `BeginRegistration`/`FinishRegistration` request payload before allowing a new WebAuthn credential to be enrolled, mirroring the pattern already used for password changes and API token deletion. Enforce this check server-side in `WebAuthnController`, not only in the Operator UI.

### Proof of Concept
1. Obtain a valid session cookie or API token for a target chainlink node user (e.g., via XSS in the Operator UI, or a copied/leaked cookie).
2. Call `POST /v2/webauthn/register` (BeginRegistration) using only that session cookie/token — no password field is required.
3. Complete `POST /v2/webauthn/register?...` (FinishRegistration) with an attacker-controlled WebAuthn credential/authenticator response.
4. The attacker's key is now a valid registered MFA credential on the victim's account, confirmed via `sessions.AddCredentialToUser`, without ever supplying the account password — unlike the equivalent password-change (`/v2/user/password`) or API-token-deletion flows, which reject the request unless the correct current password is supplied. [5](#0-4) 

**Caveat:** I was unable to locate the exact route registration/middleware line for `/v2/webauthn/register` in `core/web/router.go` (it is registered elsewhere in `v2Routes`, which I couldn't fully inspect due to iteration limits), so I cannot 100% confirm whether it's protected by `AuthenticateBySession` only vs. both session+token auth methods. This does not change the core finding — regardless of which auth method grants access, no password re-check occurs in the handler itself.

### Citations

**File:** core/web/webauthn_controller.go (L32-60)
```go
func (w *WebAuthnController) BeginRegistration(c *gin.Context) {
	ctx := c.Request.Context()
	user, ok := auth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}

	orm := w.App.AuthenticationProvider()
	uwas, err := orm.GetUserWebAuthn(ctx, user.Email)
	if err != nil {
		w.App.GetLogger().Errorf("failed to obtain current user MFA tokens: error in GetUserWebAuthn: %+v", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to register key"))
		return
	}

	webAuthnConfig := w.App.GetWebAuthnConfiguration()

	options, err := w.inProgressRegistrationsStore.BeginWebAuthnRegistration(*user, uwas, webAuthnConfig)
	if err != nil {
		w.App.GetLogger().Errorf("error in BeginWebAuthnRegistration: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}

	optionsp := presenters.NewRegistrationSettings(*options)

	jsonAPIResponse(c, optionsp, "settings")
}
```

**File:** core/web/webauthn_controller.go (L62-92)
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
```

**File:** core/web/user_controller.go (L210-229)
```go
	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to update password"))
		return
	}
	if !utils.CheckPasswordHash(request.OldPassword, string(user.HashedPassword)) {
		u.App.GetAuditLogger().Audit(audit.PasswordResetAttemptFailedMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusConflict, errors.New("old password does not match"))
		return
	}
```

**File:** core/web/user_controller.go (L297-317)
```go
	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to delete API token"))
		return
	}
	err = u.App.AuthenticationProvider().TestPassword(ctx, sessionUser.Email, request.Password)
	if err != nil {
		u.App.GetAuditLogger().Audit(audit.APITokenDeleteAttemptPasswordMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusUnauthorized, errors.New("incorrect password"))
		return
	}
```

**File:** core/web/resolver/mutation.go (L959-966)
```go
	if err = r.App.AuthenticationProvider().ClearNonCurrentSessions(ctx, session.SessionID); err != nil {
		return nil, clearSessionsError{}
	}

	err = r.App.AuthenticationProvider().SetPassword(ctx, &dbUser, args.Input.NewPassword)
	if err != nil {
		return nil, failedPasswordUpdateError{}
	}
```
