### Title
Unauthenticated External Initiator Requests Can Leak Internal Error Details Through the Auth Middleware - ([File: core/web/auth/auth.go])

### Summary
`AuthenticateExternalInitiator` in `core/web/auth/auth.go` does not fully classify errors returned by the datastore lookup. Any error other than `sql.ErrNoRows` is wrapped and propagated verbatim up through the `Authenticate` middleware, which serializes `err.Error()` directly into the HTTP response body sent to the unauthenticated caller.

### Finding Description
`AuthenticateExternalInitiator` builds an `auth.Token` from the `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` request headers and looks up the corresponding `ExternalInitiator` record: [1](#0-0) 

Only `sql.ErrNoRows` is normalized to the generic `auth.ErrorAuthFailed`. Any other error from `store.FindExternalInitiator` (e.g. a database connection error, timeout, or driver-specific error) is wrapped with `errors.Wrap(err, "finding external initiator")` and returned as-is.

The `Authenticate` middleware then treats this wrapped error specially: because it is not `auth.ErrorAuthFailed`, the method loop `break`s immediately (skipping any remaining auth methods) and passes the raw error straight to `jsonAPIError`: [2](#0-1) 

`jsonAPIError` (duplicated in `core/web/auth/helpers.go` and `core/web/helpers.go`) serializes `err.Error()` directly into the JSON response body returned to the caller: [3](#0-2) 

This is the same class of bug the external report describes ("Incomplete Error Handling" — insufficient differentiation/handling of failure paths leads to unclear or leaking information to callers), applied here to an unprivileged, unauthenticated code path: any client can send arbitrary `X-Chainlink-EA-AccessKey` headers to any endpoint guarded by `AuthenticateExternalInitiator` without any prior authentication.

### Impact Explanation
An unauthenticated attacker who can trigger a non-`ErrNoRows` datastore error (e.g. by supplying malformed/oversized header values that cause a driver-level error, or during transient DB issues) receives the raw wrapped error text in the HTTP response. This can disclose internal implementation details (SQL driver messages, connection info fragments) to an unprivileged actor, aiding further reconnaissance/exploitation. It is a defense-in-depth / information-disclosure issue rather than a direct authentication bypass, so impact is Low-Medium.

### Likelihood Explanation
Likelihood is moderate: triggering a non-`ErrNoRows` error deterministically requires specific backend conditions (DB errors, timeouts, or driver-specific input handling), so it is not trivially reproducible on every request, but it is reachable by any unauthenticated client without credentials since `AuthenticateExternalInitiator` is invoked before any successful authentication.

### Recommendation
In `AuthenticateExternalInitiator`, avoid returning the raw wrapped datastore error to the HTTP layer. Log the detailed error server-side and return a generic `auth.ErrorAuthFailed` (or another sanitized error) to the client for all datastore failure paths, consistent with how `AuthenticateByToken` handles `FindUserByAPIToken` errors. More broadly, `jsonAPIError` should avoid echoing raw internal error strings for non-4xx/validation errors; consider returning generic messages for `5xx`-class failures while logging full details server-side.

### Proof of Concept
1. Send an HTTP request to any endpoint protected by `webauth.Authenticate(..., webauth.AuthenticateExternalInitiator)` with headers:
   - `X-Chainlink-EA-AccessKey: abracadabra`
   - `X-Chainlink-EA-Secret: opensesame`
2. If the underlying `FindExternalInitiator` datastore call fails with an error other than "no rows" (e.g. simulate via a DB-level fault injection, oversized key causing query error, or connection pool exhaustion), the middleware short-circuits at `core/web/auth/auth.go:159-163` and calls `jsonAPIError(c, http.StatusUnauthorized, err)`.
3. The JSON response body will contain `err.Error()` — e.g. `"finding external initiator: <raw driver error>"` — directly visible to the unauthenticated caller, confirming the information leak.

### Citations

**File:** core/web/auth/auth.go (L119-133)
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
```

**File:** core/web/auth/auth.go (L153-173)
```go
// Authenticate is middleware which authenticates the request by attempting to
// authenticate using all the provided methods.
func Authenticate(store Authenticator, methods ...authMethod) gin.HandlerFunc {
	return func(c *gin.Context) {
		var err error
		for _, method := range methods {
			err = method(c, store)
			if !errors.Is(err, auth.ErrorAuthFailed) {
				break
			}
		}
		if err != nil {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, err)

			return
		}

		c.Next()
	}
}
```

**File:** core/web/auth/helpers.go (L15-23)
```go
func jsonAPIError(c *gin.Context, statusCode int, err error) {
	_ = c.Error(err).SetType(gin.ErrorTypePublic)
	var jsonErr *models.JSONAPIErrors
	if errors.As(err, &jsonErr) {
		c.JSON(statusCode, jsonErr)
		return
	}
	c.JSON(statusCode, models.NewJSONAPIErrorsWith(err.Error()))
}
```
