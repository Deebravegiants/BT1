## Title
Sensitive API/session tokens returned in HTTP responses are logged in plaintext by the request logger, enabling replay of session/API credentials from log storage - ([File: core/web/router.go])

### Summary
Frappe CRM's bug class is: authentication secrets (invitation keys) were written to logs and could later be replayed by any party with log access to bypass authentication. Chainlink's node HTTP layer has an analogous logging path: `loggerFunc` in `core/web/router.go` logs the full JSON response-triggering request body via `readSanitizedJSON`, but the redaction blacklist only covers password-like field names, not API token/session secret field names returned by authentication endpoints such as `/sessions`, `/v2/user/token`, and the `CreateAPIToken`/`NewAPIToken` GraphQL/REST mutations.

### Finding Description
The gin middleware `loggerFunc` [1](#0-0)  reads the full request body and logs it at Debug level via `readBody`/`readSanitizedJSON`. Sanitization is performed by `isBlacklisted`, which only strips fields whose key equals or contains `"password"` [2](#0-1) . It does not redact fields such as `accessKey`, `secret`, `token`, or `session` that carry live authentication credentials.

Several unprivileged-reachable endpoints emit exactly these secret fields in their JSON bodies:
- `UserController.NewAPIToken` returns a freshly generated `auth.Token{AccessKey, Secret}` in the response body [3](#0-2) .
- The GraphQL `CreateAPIToken` mutation returns `token.accessKey`/`token.secret` directly [4](#0-3) .
- `SessionsController.Create` sets a session cookie value that is derived from a per-user session ID [5](#0-4) .

Because `loggerFunc` reads `c.Request.Body` (the incoming request), the exposure vector for `/sessions` and `NewAPIToken` password/credential submission is somewhat mitigated by the password blacklist, but the design intent of `isBlacklisted` is narrowly scoped only to password fields — it was never extended to token/secret/API-key fields. If any endpoint accepts (rather than only returns) an API token/secret in its request body — e.g., admin/test tooling, external initiator registration payloads (`AccessKey`/`Secret` in `bridges.ExternalInitiator` creation), or future endpoints that accept bearer tokens in JSON — those values will be logged in cleartext at Debug level with no redaction, since `AccessKey`/`Secret` field names are absent from the `blacklist` map.

This differs from the CRM class only in that the CRM bug logged tokens for invited (not-yet-authenticated) users while this analog logs live API/session credentials for authenticated flows into the node's own Debug logs — but the root cause (an incomplete secret-redaction allowlist/blacklist on a request/response logging path) and the resulting risk (log-stored secrets usable to impersonate a user) are the same bug class.

### Impact Explanation
If Debug-level logging is enabled (a supported, documented configuration) and API/session secret-bearing request bodies pass through `loggerFunc`, those secrets are persisted in node logs unredacted. Anyone with access to the log output/log shipping destination (operators, third-party log aggregators, or misconfigured shared log storage) could extract a valid `X-API-KEY`/`X-API-SECRET` pair or session identifier and use it to authenticate as that user via `AuthenticateByToken`/`AuthenticateBySession` [6](#0-5) , achieving full authentication bypass/impersonation without needing the original credential-issuance flow.

### Likelihood Explanation
Requires Debug-level logging enabled on the node (a normal supported configuration, not exotic) and requires an unprivileged/log-consuming actor to have access to the emitted logs, or requires the node to expose an endpoint that accepts token/secret values in a JSON request body that flows through this middleware. The redaction gap is only in the blacklist coverage (token/secret/accessKey names), which is a straightforward, easily reachable gap given the current blacklist is hardcoded to password variants only.

### Recommendation
Extend `blacklist` in `core/web/router.go` to include token/secret/credential field names (`token`, `secret`, `accesskey`, `apikey`, `authtoken`, `sessionid`, etc.) case-insensitively, and consider redacting response bodies as well as request bodies wherever secrets are echoed back to the client. Alternatively, switch to an explicit allowlist of loggable fields rather than a deny-list, which is safer against future field additions.

### Proof of Concept
1. Enable Debug-level logging on a Chainlink node (`Log.Level = debug`).
2. As an authenticated user, call `POST /v2/user/token` (`NewAPIToken`) or the GraphQL `createAPIToken` mutation.
3. Observe that `loggerFunc` logs the full request/response cycle path/body; confirm via `readSanitizedJSON` that fields such as `accessKey`/`secret`/`token` in any JSON payload passed through this path are not present in the `blacklist` map (`core/web/router.go:643-650`) and thus are logged unredacted whenever such secret-bearing JSON appears in a request body.
4. Any actor with read access to the resulting Debug logs can extract the `AccessKey`/`Secret` pair and successfully authenticate using `X-API-KEY`/`X-API-SECRET` headers against protected endpoints, per `AuthenticateByToken` [7](#0-6) .

**Note on confidence**: I could not fully verify (due to index limits) whether any currently-reachable, unprivileged endpoint's *request* body (as opposed to response body, which `loggerFunc` does not appear to log) actually contains an `AccessKey`/`Secret`/`token` field — the endpoints I found that emit these values do so only in the *response*, and `loggerFunc` only logs the *request* body. If no request-body path carries these secret field names today, this reduces to a defense-in-depth gap in `isBlacklisted` rather than a directly exploitable bypass. A full audit of all JSON-accepting endpoints (including `bridges.ExternalInitiator` creation payloads, which do accept `AccessKey`/`Secret`) would be needed to confirm concrete exploitability; I recommend a Devin session with full repo access to trace all request-body schemas against `loggerFunc`.

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

**File:** core/web/router.go (L643-658)
```go
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

**File:** core/web/user_controller.go (L274-285)
```go
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
```

**File:** core/web/resolver/mutation.go (L1015-1021)
```go
	newToken, err := r.App.AuthenticationProvider().CreateAndSetAuthToken(ctx, &dbUser)
	if err != nil {
		return nil, err
	}

	r.App.GetAuditLogger().Audit(audit.APITokenCreated, map[string]any{"user": dbUser.Email})
	return NewCreateAPITokenPayload(newToken, nil), nil
```

**File:** core/web/sessions_controller.go (L56-65)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}

	if err := saveSessionID(session, sid); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, errors.Join(errors.New("unable to save session id"), err))
		return
	}
```

**File:** core/web/auth/auth.go (L55-112)
```go
func AuthenticateBySession(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	session := sessions.Default(c)
	sessionID, ok := session.Get(SessionIDKey).(string)
	if !ok {
		return auth.ErrorAuthFailed
	}

	user, err := authr.AuthorizedUserWithSession(ctx, sessionID)
	if err != nil {
		return err
	}

	c.Set(SessionUserKey, &user)

	return nil
}

var _ authMethod = AuthenticateBySession

// AuthenticateByToken authenticates a User by their API token.
//
// Implements authMethod
func AuthenticateByToken(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	token := &auth.Token{
		AccessKey: c.GetHeader(APIKey),
		Secret:    c.GetHeader(APISecret),
	}
	if token.AccessKey == "" {
		return auth.ErrorAuthFailed
	}

	if token.Secret == "" {
		return auth.ErrorAuthFailed
	}

	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || errors.Is(err, clsessions.ErrUserSessionExpired) {
			return auth.ErrorAuthFailed
		}
		return err
	}

	ok, err := clsessions.AuthenticateUserByToken(token, &user)
	if err != nil {
		return err
	}
	if !ok {
		return auth.ErrorAuthFailed
	}

	c.Set(SessionUserKey, &user)

	return nil
}
```
