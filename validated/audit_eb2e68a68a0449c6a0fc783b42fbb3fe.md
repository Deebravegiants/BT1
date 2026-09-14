### Title
`ExternalInitiatorsEnabled` config flag disables initiator *creation* only, not authentication/job-run triggering - ([File: core/web/external_initiators_controller.go], [File: core/web/auth/auth.go])

### Summary
The `JobPipeline.ExternalInitiatorsEnabled` configuration flag is intended to disable the External Initiator feature. However, the check is only performed in `ExternalInitiatorsController.Create`, which gates the creation of new external initiator credentials. The actual authentication/authorization path used to *use* an external initiator to trigger job runs, `AuthenticateExternalInitiator` in `core/web/auth/auth.go`, never checks this flag. This is structurally identical to the Rubicon `buyEnabled` bug: a "disable" flag is checked in the wrong function, so it fails to disable the feature end-to-end.

### Finding Description
`ExternalInitiatorsController.Create` explicitly rejects new external initiator creation when the flag is off: [1](#0-0) 

But the runtime authentication path that actually allows an external initiator (an unprivileged, remote actor holding an access key/secret pair) to authenticate and trigger job runs is implemented in `AuthenticateExternalInitiator`, which only checks the access-key/secret pair against the stored `bridges.ExternalInitiator` record — it never consults `ExternalInitiatorsEnabled`: [2](#0-1) 

The lookup helper `FindExternalInitiator`, implemented separately in each authentication provider (local, LDAP, OIDC), similarly performs no enabled-flag check: [3](#0-2) [4](#0-3) [5](#0-4) 

This mirrors exactly the Rubicon report's pattern: the `require(buyEnabled)` guard was placed inside `_buys` (only one code path to reach `buy`), so when the other code path (`matchingEnabled == false`) was taken, the guard never executed and buys could not be disabled. Here, the `ExternalInitiatorsEnabled` guard is placed only in the `Create` handler (the "provisioning" path), while the authentication/run-triggering path (`AuthenticateExternalInitiator` → job run trigger) is a completely separate code path that never checks the flag. As a result, toggling `ExternalInitiatorsEnabled = false` after initiators already exist (or were created while it was previously `true`) does **not** actually disable the feature — external initiators already in the `external_initiators` table can continue to authenticate and trigger job runs indefinitely.

### Impact Explanation
An operator who disables `ExternalInitiatorsEnabled` believes that the External Initiator attack surface (an internet-facing, unprivileged, header/access-key based authentication mechanism that grants effective `Run` role via `c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})`) is turned off. In reality, any external initiator credentials created prior to disabling the flag remain fully functional, allowing an external, unprivileged holder of those credentials to continue authenticating and triggering job runs. This is a config/expectation bypass of an authentication-disable control, effectively an unauthorized-run-trigger capability that the operator explicitly intended to shut off.

### Likelihood Explanation
Likelihood is moderate: exploitation requires that valid external initiator credentials already exist (created while the feature was enabled) and that an operator later disables the feature expecting it to fully cut off external initiator access. This is a realistic operational scenario (disabling a feature as an incident-response/mitigation action), and the flag's name and the `Create` handler's error message ("The External Initiator feature is disabled by configuration") strongly suggest the intended semantics are a full feature kill-switch, not merely "no new initiators."

### Recommendation
Move (or duplicate) the `ExternalInitiatorsEnabled` check into `AuthenticateExternalInitiator` in `core/web/auth/auth.go` (and/or into the `FindExternalInitiator` implementations) so that authentication attempts are rejected whenever the feature is disabled, regardless of whether the initiator record was created earlier. This ensures the kill-switch actually revokes access end-to-end rather than only blocking new provisioning.

### Proof of Concept
1. Start a node with `JobPipeline.ExternalInitiatorsEnabled = true`.
2. Create an external initiator via `POST /v2/external_initiators` and record the returned `AccessKey`/`Secret` (see `ExternalInitiatorsController.Create`, `core/web/external_initiators_controller.go:62-100`).
3. Operator sets `JobPipeline.ExternalInitiatorsEnabled = false` and restarts/reloads the node, intending to fully disable the External Initiator feature.
4. Attempt to create a new external initiator — confirmed blocked with `405 Method Not Allowed`, as expected.
5. Using the previously obtained credentials, send a request to an endpoint protected by `webauth.Authenticate(..., webauth.AuthenticateExternalInitiator)` (e.g. the job-run trigger endpoint) with headers `X-Chainlink-EA-AccessKey` / `X-Chainlink-EA-Secret` set to the values from step 2.
6. `AuthenticateExternalInitiator` (`core/web/auth/auth.go:119-149`) calls `FindExternalInitiator` and `bridges.AuthenticateExternalInitiator`, both of which succeed because neither checks `ExternalInitiatorsEnabled`. The request is authenticated with `UserRoleRun`, and the job run proceeds — demonstrating the "disabled" feature is still fully functional for existing credentials.

### Citations

**File:** core/web/external_initiators_controller.go (L62-69)
```go
func (eic *ExternalInitiatorsController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	eir := &bridges.ExternalInitiatorRequest{}
	if !eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled() {
		err := errors.New("The External Initiator feature is disabled by configuration")
		jsonAPIError(c, http.StatusMethodNotAllowed, err)
		return
	}
```

**File:** core/web/auth/auth.go (L116-149)
```go
// AuthenticateExternalInitiator authenticates an external initiator request.
//
// Implements authMethod
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

**File:** core/sessions/localauth/orm.go (L364-372)
```go
// NOTE: this is duplicated from the bridges ORM to appease the AuthStorer interface
func (o *orm) FindExternalInitiator(
	ctx context.Context,
	eia *auth.Token,
) (*bridges.ExternalInitiator, error) {
	exi := &bridges.ExternalInitiator{}
	err := o.ds.GetContext(ctx, exi, `SELECT * FROM external_initiators WHERE access_key = $1`, eia.AccessKey)
	return exi, err
}
```

**File:** core/sessions/ldapauth/ldap.go (L615-620)
```go
// FindExternalInitiator supports the 'Run' role external initiator header auth functionality
func (l *ldapAuthenticator) FindExternalInitiator(ctx context.Context, eia *auth.Token) (*bridges.ExternalInitiator, error) {
	exi := &bridges.ExternalInitiator{}
	err := l.ds.GetContext(ctx, exi, `SELECT * FROM external_initiators WHERE access_key = $1`, eia.AccessKey)
	return exi, err
}
```

**File:** core/sessions/oidcauth/oidc.go (L571-576)
```go
// FindExternalInitiator supports the 'Run' role external initiator header auth functionality
func (oi *oidcAuthenticator) FindExternalInitiator(ctx context.Context, eia *auth.Token) (*bridges.ExternalInitiator, error) {
	exi := &bridges.ExternalInitiator{}
	err := oi.ds.GetContext(ctx, exi, `SELECT * FROM external_initiators WHERE access_key = $1`, eia.AccessKey)
	return exi, err
}
```
