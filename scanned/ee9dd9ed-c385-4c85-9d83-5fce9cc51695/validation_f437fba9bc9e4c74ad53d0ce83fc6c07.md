### Title
`AuthenticateExternalInitiator` performs no empty-credential check before querying and comparing initiator secrets, unlike token auth - (File: `core/web/auth/auth.go`)

### Summary
The external report describes a constructor that accepts a null/zero `merchant` address with no sanity check, leaving the contract in a permanently broken/undefined state. The closest reachable analog in this codebase is in the node's external-initiator authentication path: `AuthenticateByToken` explicitly rejects empty `AccessKey`/`Secret` values before doing any lookup or comparison, but the parallel `AuthenticateExternalInitiator` function omits this same guard, sending an unvalidated (potentially empty-string) credential straight into the datastore lookup and secret comparison.

### Finding Description
`AuthenticateByToken` in `core/web/auth/auth.go` builds an `auth.Token` from the `X-API-KEY`/`X-API-SECRET` headers and immediately validates both fields are non-empty before calling `FindUserByAPIToken`: [1](#0-0) 

By contrast, `AuthenticateExternalInitiator` builds the equivalent `auth.Token` from the `ExternalInitiatorAccessKeyHeader`/`ExternalInitiatorSecretHeader` headers but has **no** such check — it passes the token, even if `AccessKey`/`Secret` are empty strings, directly to `store.FindExternalInitiator`: [2](#0-1) 

`FindExternalInitiator` performs a direct equality lookup against the `access_key` column: [3](#0-2) 

The subsequent secret check `bridges.AuthenticateExternalInitiator` compares hashed secrets in constant time, which is sound in isolation: [4](#0-3) 

The root cause mirrors the reported bug class: a critical identity/credential field (`merchant` address in the report; `AccessKey`/`Secret` here) is never checked against its "null"/empty sentinel value before being used to establish identity or trust, whereas the sibling authentication path (`AuthenticateByToken`) treats that same sentinel value as an explicit failure condition. This is a defense-in-depth gap in the internet-facing authentication middleware (`core/web/auth`), which is invoked on every unprivileged HTTP request when `AuthenticateExternalInitiator` is included in an endpoint's `Authenticate(...)` method chain.

### Impact Explanation
Practically, this is a robustness/defense-in-depth gap rather than a directly demonstrated bypass: `access_key` in Postgres is unlikely to ever be stored as an empty string because `bridges.NewExternalInitiator` always generates a random `AccessKey` via `auth.NewToken()` in the standard controller path. However, unlike `merchant == 0x0` in Solidity (which is a hard invariant break), the missing guard here means that if any code path (migrations, admin tooling, test/ops scripts, or future refactors) ever creates or updates an `ExternalInitiator` row with a blank/null `access_key`/`hashed_secret`, an attacker could authenticate as that external initiator using empty headers, inheriting the `UserRoleRun` role and its ability to trigger job runs. The missing check removes the same "fail fast, fail loudly" safety net that exists one function away (`AuthenticateByToken`), so the code is not defensively hardened against this scenario the way its sibling is.

### Likelihood Explanation
Low-to-Medium: exploitation requires an external-initiator record with an empty `AccessKey`/`HashedSecret`, which is not currently produced by the standard `POST /v2/external_initiators` flow (`ExternalInitiatorsController.Create` always calls `bridges.NewExternalInitiator`, which always generates random values). No currently-reachable code path was found that persists an `ExternalInitiator` with a blank `AccessKey` via the HTTP API. The vulnerability is latent/defense-in-depth rather than immediately triggerable through the public API today.

### Recommendation
Add the same explicit empty-value checks used in `AuthenticateByToken` to `AuthenticateExternalInitiator`:
```go
if eia.AccessKey == "" || eia.Secret == "" {
    return auth.ErrorAuthFailed
}
```
placed before the call to `store.FindExternalInitiator`, so that empty/null credentials are rejected outright regardless of what is stored in the database, consistent with the "fail as early and loudly as possible" principle cited in the original report.

### Proof of Concept
1. Compare the two authentication functions in `core/web/auth/auth.go`:
   - `AuthenticateByToken` (lines 78-90) rejects empty `AccessKey`/`Secret` before any DB lookup.
   - `AuthenticateExternalInitiator` (lines 119-133) has no equivalent rejection and proceeds straight to `store.FindExternalInitiator(ctx, eia)` with whatever (possibly empty) values were supplied in the request headers.
2. If a `bridges.ExternalInitiator` row ever exists with `access_key = ''` (e.g., through direct DB manipulation, a future migration, or an ORM path that bypasses `NewExternalInitiator`, such as the test helper pattern seen in `core/web/external_initiators_controller_test.go` lines 210-214 where an `ExternalInitiator{Name: "abracadabra"}` is inserted with no `AccessKey` set), an attacker sending requests with empty `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers would pass `FindExternalInitiator` and reach `bridges.AuthenticateExternalInitiator`, inheriting `UserRoleRun`.

### Citations

**File:** core/web/auth/auth.go (L78-90)
```go
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
```

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

**File:** core/bridges/orm.go (L262-267)
```go
// FindExternalInitiator finds an external initiator given an authentication request
func (o *orm) FindExternalInitiator(ctx context.Context, eia *auth.Token) (*ExternalInitiator, error) {
	exi := &ExternalInitiator{}
	err := o.ds.GetContext(ctx, exi, `SELECT * FROM external_initiators WHERE access_key = $1`, eia.AccessKey)
	return exi, err
}
```

**File:** core/bridges/external_initiator.go (L59-67)
```go
// AuthenticateExternalInitiator compares an auth against an initiator and
// returns true if the password hashes match
func AuthenticateExternalInitiator(eia *auth.Token, ea *ExternalInitiator) (bool, error) {
	hashedSecret, err := auth.HashedSecret(eia, ea.Salt)
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hashedSecret), []byte(ea.HashedSecret)) == 1, nil
}
```
