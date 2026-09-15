## Title
Sensitive credentials (API/EA secrets, tokens) logged in plaintext via request-body logging middleware - ([File: core/web/router.go])

### Summary
The Gin request-logging middleware `loggerFunc` logs the full JSON request body for every API call, passing it through `readBody`/`readSanitizedJSON`, which redacts only a small, hardcoded blacklist of field names (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`) or any key containing the substring "password". [1](#0-0) [2](#0-1)  Any other sensitive credential field submitted in a request body—access keys, secrets, tokens, or WebAuthn attestation data—is logged verbatim at Debug level.

### Finding Description
`readSanitizedJSON` walks the top-level JSON keys of the request body and only redacts entries matching the `blacklist` map or containing "password" as a substring: [3](#0-2) . Numerous unprivileged-reachable endpoints accept sensitive secrets as JSON body fields that are not covered by this blacklist, e.g.:
- `SessionRequest` login body includes `WebAuthnData` (the WebAuthn attestation/assertion blob) submitted during MFA login, processed in `CreateSession`. [4](#0-3) 
- `ExternalInitiatorRequest`/response bodies exchange `AccessKey`, `Secret`, `OutgoingToken`, `OutgoingSecret` for external initiators created via `ExternalInitiatorsController.Create`. [5](#0-4) [6](#0-5) 
- `ChangeAuthTokenRequest`/`auth.Token` for creating/deleting user API tokens (`NewAPIToken`/`DeleteAPIToken`), where the response body (`auth.Token{AccessKey, Secret}`) is not redacted either. [7](#0-6) 

Because `loggerFunc` only reads and sanitizes the *request* body via `readBody(rdr, lggr)` (line 562), and the blacklist only matches password-like keys, any request carrying `accessKey`, `secret`, `outgoingToken`, `outgoingSecret`, or `webAuthnData` fields is written unredacted into the node's Debug logs.

### Impact Explanation
If Debug-level logging is enabled (a supported, documented configuration) or logs are aggregated/forwarded (e.g. to a SIEM, file, or third-party log service as the audit logger already does for other events), an operator, log-shipping pipeline, or anyone with read access to node logs can recover external-initiator credentials, WebAuthn assertion data, or other secrets submitted by legitimate unprivileged/legitimate clients. This mirrors the underlying risk pattern in the report (account/credential compromise leading to unauthorized session or fund-moving actions): leaked EA `AccessKey`/`Secret` pairs allow an attacker to impersonate the external initiator and trigger job runs (`AuthenticateExternalInitiator` grants the `Run` role solely based on possessing these values). [8](#0-7) 

### Likelihood Explanation
Requires Debug logging enabled or log exfiltration/access, which is a realistic operational configuration (not a mocked-only or dev-only path) and does not require any additional privilege beyond making a normal authenticated-but-unprivileged create/rotate-token request that any external-initiator management user is expected to perform. The blacklist mechanism is clearly incomplete by design (substring match on "password" only), making this a systemic redaction gap rather than a one-off oversight.

### Recommendation
Expand the redaction blacklist in `isBlacklisted`/`blacklist` (core/web/router.go) to cover credential-bearing keys case-insensitively, e.g. `secret`, `accesskey`, `incomingsecret`, `outgoingsecret`, `outgoingtoken`, `apitoken`, `webauthndata`, `token`. Consider switching from a denylist to an allowlist of safe-to-log fields, and additionally sanitize response bodies (not just request bodies) since several of these secrets are returned to the client in the response payload.

### Proof of Concept
1. Enable Debug-level logging on a chainlink node.
2. Call `POST /v2/external_initiators` with a valid admin/edit session to create an external initiator (`ExternalInitiatorsController.Create`).
3. Observe the Debug log entry emitted by `loggerFunc`: the `body` field contains the raw JSON request, and because `AccessKey`/`Secret`/`OutgoingToken`/`OutgoingSecret` fields are not in the redaction blacklist, they appear unredacted in node logs alongside the response also containing these values.
4. Similarly, `POST /v2/user/token` (NewAPIToken) or WebAuthn login submissions leak `password`-adjacent but distinctly-named secret fields (e.g., `webAuthnData`) through the same unredacted logging path.

### Citations

**File:** core/web/router.go (L534-568)
```go
func loggerFunc(lggr logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		buf, err := io.ReadAll(c.Request.Body)
		if err != nil {
			lggr.Error("Web request log error: ", err.Error())
			// Implicitly relies on limits.RequestSizeLimiter
			// overriding of c.Request.Body to abort gin's Context
			// inside io.ReadAll.
			// Functions as we would like, but horrible from an architecture
			// and design pattern perspective.
			if !c.IsAborted() {
				c.AbortWithStatus(http.StatusBadRequest)
			}
			return
		}
		rdr := bytes.NewBuffer(buf)
		c.Request.Body = io.NopCloser(bytes.NewBuffer(buf))

		start := time.Now()
		c.Next()
		end := time.Now()

		lggr.Debugw(fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path),
			"method", c.Request.Method,
			"status", c.Writer.Status(),
			"path", c.Request.URL.Path,
			"ginPath", c.FullPath(),
			"query", redact(c.Request.URL.Query()),
			"body", readBody(rdr, lggr),
			"clientIP", c.ClientIP(),
			"errors", c.Errors.String(),
			"servedAt", end.Format("2006-01-02 15:04:05"),
			"latency", fmt.Sprintf("%v", end.Sub(start)),
		)
	}
```

**File:** core/web/router.go (L608-658)
```go
func readSanitizedJSON(buf *bytes.Buffer) (string, error) {
	var dst map[string]any
	err := json.Unmarshal(buf.Bytes(), &dst)
	if err != nil {
		return "", err
	}

	cleaned := map[string]any{}
	for k, v := range dst {
		if isBlacklisted(k) {
			cleaned[k] = "*REDACTED*"
			continue
		}
		cleaned[k] = v
	}

	b, err := json.Marshal(cleaned)
	if err != nil {
		return "", err
	}
	return string(b), err
}

func redact(values url.Values) string {
	cleaned := url.Values{}
	for k, v := range values {
		if isBlacklisted(k) {
			cleaned[k] = []string{"REDACTED"}
			continue
		}
		cleaned[k] = v
	}
	return cleaned.Encode()
}

// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```

**File:** core/web/sessions_controller.go (L29-68)
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

	if err := saveSessionID(session, sid); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, errors.Join(errors.New("unable to save session id"), err))
		return
	}

	jsonAPIResponse(c, Session{Authenticated: true}, "session")
}
```

**File:** core/web/external_initiators_controller.go (L61-100)
```go
// Create builds and saves a new external initiator
func (eic *ExternalInitiatorsController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	eir := &bridges.ExternalInitiatorRequest{}
	if !eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled() {
		err := errors.New("The External Initiator feature is disabled by configuration")
		jsonAPIError(c, http.StatusMethodNotAllowed, err)
		return
	}

	eia := auth.NewToken()
	if err := c.ShouldBindJSON(eir); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	ei, err := bridges.NewExternalInitiator(eia, eir)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	if err := ValidateExternalInitiator(ctx, eir, eic.App.BridgeORM()); err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}
	if err := eic.App.BridgeORM().CreateExternalInitiator(ctx, ei); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	eic.App.GetAuditLogger().Audit(audit.ExternalInitiatorCreated, map[string]any{
		"externalInitiatorID":   ei.ID,
		"externalInitiatorName": ei.Name,
		"externalInitiatorURL":  ei.URL,
	})

	resp := presenters.NewExternalInitiatorAuthentication(*ei, *eia)
	jsonAPIResponseWithStatus(c, resp, "external initiator authentication", http.StatusCreated)
}
```

**File:** core/web/presenters/external_initiators.go (L12-38)
```go
// ExternalInitiatorAuthentication includes initiator and authentication details.
type ExternalInitiatorAuthentication struct {
	Name           string        `json:"name,omitempty"`
	URL            models.WebURL `json:"url"`
	AccessKey      string        `json:"incomingAccessKey,omitempty"`
	Secret         string        `json:"incomingSecret,omitempty"`
	OutgoingToken  string        `json:"outgoingToken,omitempty"`
	OutgoingSecret string        `json:"outgoingSecret,omitempty"`
}

// NewExternalInitiatorAuthentication creates an instance of ExternalInitiatorAuthentication.
func NewExternalInitiatorAuthentication(
	ei bridges.ExternalInitiator,
	eia auth.Token,
) *ExternalInitiatorAuthentication {
	var result = &ExternalInitiatorAuthentication{
		Name:           ei.Name,
		AccessKey:      ei.AccessKey,
		Secret:         eia.Secret,
		OutgoingToken:  ei.OutgoingToken,
		OutgoingSecret: ei.OutgoingSecret,
	}
	if ei.URL != nil {
		result.URL = *ei.URL
	}
	return result
}
```

**File:** core/web/user_controller.go (L243-286)
```go
// NewAPIToken generates a new API token for a user overwriting any pre-existing one set.
func (u *UserController) NewAPIToken(c *gin.Context) {
	ctx := c.Request.Context()
	var request clsession.ChangeAuthTokenRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

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
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to create API token"))
		return
	}
	// In order to create an API token, login validation with provided password must succeed
	err = u.App.AuthenticationProvider().TestPassword(ctx, sessionUser.Email, request.Password)
	if err != nil {
		u.App.GetAuditLogger().Audit(audit.APITokenCreateAttemptPasswordMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusUnauthorized, errors.New("incorrect password"))
		return
	}
	newToken := auth.NewToken()
	if err := u.App.AuthenticationProvider().SetAuthToken(ctx, &user, newToken); err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	u.App.GetAuditLogger().Audit(audit.APITokenCreated, map[string]any{"user": user.Email})
	jsonAPIResponseWithStatus(c, newToken, "auth_token", http.StatusCreated)
}
```

**File:** core/web/auth/auth.go (L119-149)
```go
func AuthenticateExternalInitiator(c *gin.Context, store Authenticator) error {
	ctx := c.Request.Context()
	eia := &auth.Token{
		AccessKey: c.GetHeader(static.ExternalInitiatorAccessKeyHeader),
		Secret:    c.GetHeader(static.ExternalInitiatorSecretHeader),
	}

	ei, err := store.FindExternalInitiator(ctx, eia)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return auth.ErrorAuthFailed
		}

		return errors.Wrap(err, "finding external initiator")
	}

	ok, err := bridges.AuthenticateExternalInitiator(eia, ei)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	// External initiator endpoints (wrapped with AuthenticateExternalInitiator) inherently assume the role
	// of 'run' (required to trigger job runs)
	c.Set(SessionExternalInitiatorKey, ei)
	c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})

	return nil
}
```
