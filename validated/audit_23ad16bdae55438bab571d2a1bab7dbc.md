### Title
Authentication middleware leaks raw database error details to unauthenticated clients - ([File: core/web/auth/auth.go])

### Summary
`AuthenticateExternalInitiator` propagates raw underlying datastore errors (wrapped, not sanitized) up through the authentication middleware chain to the HTTP response body sent to the unauthenticated caller, mirroring the CVE-2019-16768 pattern where internal exception details are wrapped and surfaced to the user during login/authentication.

### Finding Description
`AuthenticateExternalInitiator` calls `store.FindExternalInitiator(ctx, eia)`, and only swallows the error into a generic `auth.ErrorAuthFailed` when it is exactly `sql.ErrNoRows`. Any other error (e.g. a database connectivity/driver error, timeout, malformed query response, etc.) is instead wrapped with `errors.Wrap(err, "finding external initiator")` and returned as-is: [1](#0-0) 

This error bubbles up through the `Authenticate` middleware, which — since it is not `auth.ErrorAuthFailed` — is passed directly into `jsonAPIError(c, http.StatusUnauthorized, err)`: [2](#0-1) 

`jsonAPIError` serializes `err.Error()` verbatim into the JSON response body returned to the caller: [3](#0-2) 

The underlying `FindExternalInitiator` implementation performs a direct SQL query with no wrapping/sanitization at the ORM layer, so any driver-level error message (e.g., connection failures, column/type mismatches, SQL driver internals) flows through unmodified: [4](#0-3) 

This is the same bug class as CVE-2019-16768: an authentication code path wraps an internal/system exception and lets its message reach the end user in the HTTP response, rather than logging it server-side and returning a generic error.

### Impact Explanation
An unauthenticated caller hitting an external-initiator-protected endpoint (sending `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers) can trigger this path. If any underlying datastore error other than "no rows" occurs, the raw error text (potentially including internal details such as DB driver identifiers, connection info, or query context) is returned in the JSON error body. This is an information-disclosure issue rather than a full authentication bypass — impact is limited to leakage of internal system details that could aid further attacks, consistent with the "Medium/C:L" severity of the original CVE.

### Likelihood Explanation
Likelihood of hitting non-`sql.ErrNoRows` errors organically is low (requires an actual DB issue such as connection pool exhaustion, timeout, or transient failure), so this is more of a hardening gap than a readily-triggerable bug in normal operation. It does not require any special privilege — any unauthenticated network client attempting external-initiator auth can potentially reach it under adverse DB conditions.

### Recommendation
In `AuthenticateExternalInitiator` (`core/web/auth/auth.go`), do not return the wrapped underlying error directly to the HTTP layer. Instead, log the detailed error server-side (as is already done elsewhere, e.g. in `core/sessions/localauth/orm.go`'s `CreateSession`) and return a generic `auth.ErrorAuthFailed` (or another opaque error) to the caller for any error path, matching the pattern used for `sql.ErrNoRows`.

### Proof of Concept
1. Configure an external initiator authentication request against an endpoint protected by `AuthenticateExternalInitiator`.
2. Cause `FindExternalInitiator`'s underlying `o.ds.GetContext` call to fail with something other than `sql.ErrNoRows` (e.g., simulate a DB connectivity blip, or a schema mismatch causing a scan error).
3. Observe the HTTP 401 response body via `jsonAPIError`: it will contain `"finding external initiator: <raw driver error message>"` instead of a generic authentication failure message, confirming information leakage to the unauthenticated client.

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

**File:** core/bridges/orm.go (L262-267)
```go
// FindExternalInitiator finds an external initiator given an authentication request
func (o *orm) FindExternalInitiator(ctx context.Context, eia *auth.Token) (*ExternalInitiator, error) {
	exi := &ExternalInitiator{}
	err := o.ds.GetContext(ctx, exi, `SELECT * FROM external_initiators WHERE access_key = $1`, eia.AccessKey)
	return exi, err
}
```
