### Title
External Initiator authentication does not check `ExternalInitiatorsEnabled` feature flag, allowing runs to be triggered after the feature is disabled - ([File: core/web/auth/auth.go])

### Summary
The reported Fei Protocol bug is a "missing post-state validation" pattern: an action-gating flag (`launch`) is checked when performing one operation (initial group setup) but is never re-checked on the follow-on operations (`purchase`, `commit`), so those operations remain reachable after the state that should have disabled them changes. The same class of bug exists in the chainlink External Initiator authentication path: creation of a new External Initiator is gated by the `ExternalInitiatorsEnabled` config flag, but the authentication method used on every subsequent request that lets an External Initiator trigger a job run does not check this flag at all.

### Finding Description
`ExternalInitiatorsController.Create` explicitly checks the feature flag before allowing a new External Initiator credential to be created: [1](#0-0) 

However, the actual authentication entrypoint that is invoked on every incoming request from an External Initiator, `AuthenticateExternalInitiator`, never checks `JobPipeline().ExternalInitiatorsEnabled()`. It only validates the access key/secret pair against previously stored initiators and, on success, immediately grants the `UserRoleRun` role, which is the role required to trigger job runs: [2](#0-1) 

This means:
- An External Initiator credential created while the feature was enabled continues to authenticate successfully and can still invoke job runs even after an operator disables the feature by setting `ExternalInitiatorsEnabled = false`.
- The `Destroy` (delete) endpoint is the only way to actually revoke access, since disabling the flag only blocks new creations, not existing credentials' use.

This directly mirrors the reported bug class: a gating check exists on the "creation"/"launch" path but is missing on the recurring operational path (`purchase`/`commit` analog = "authenticate and trigger a run"), so the feature-disable control can be silently bypassed by any holder of a previously-issued External Initiator key/secret pair — an unprivileged, non-admin actor from the node's perspective (the EI credential holder, not a local Chainlink node operator).

### Impact Explanation
If an operator disables External Initiators via config (e.g., for security/compliance reasons, incident response, or because a previously trusted external system should no longer be allowed to trigger runs), any already-issued External Initiator credential remains fully functional for authenticating requests and initiating job runs. This defeats the operator's intent of using the config flag as a kill switch and could allow unauthorized job execution (fund movement, oracle report submission, etc., depending on the job) using stale/compromised credentials that the operator believed were neutralized by disabling the feature flag — without requiring the operator to individually track down and delete every External Initiator record.

### Likelihood Explanation
Likelihood is moderate: it requires (1) External Initiators to have been enabled and at least one credential issued at some point, and (2) the operator later disabling the flag (rather than deleting the specific initiator) as their means of revocation. Since the flag is documented and exposed as the primary toggle for the feature, it is a plausible operational path, and exploitation requires no privilege beyond already possessing a previously issued (possibly leaked/rotated-away) External Initiator access key/secret — no further authentication bypass or role escalation is needed.

### Recommendation
Add a check for `JobPipeline().ExternalInitiatorsEnabled()` inside `AuthenticateExternalInitiator` (core/web/auth/auth.go) so that authentication fails immediately when the feature is disabled, regardless of whether valid credentials are presented — mirroring the recommended fix pattern of validating the gating condition at every entrypoint that performs the sensitive action, not just at credential-creation time. Alternatively/additionally, disabling the flag could cascade to revoking/deleting all existing External Initiator records so that stale credentials cannot be used to bypass the intended kill switch.

### Proof of Concept
1. Start a node with `JobPipeline.ExternalInitiatorsEnabled = true`.
2. Create an External Initiator via `POST /v2/external_initiators` (as in `ExternalInitiatorsController.Create`), capturing the returned `AccessKey`/`Secret`.
3. Operator disables the feature: set `JobPipeline.ExternalInitiatorsEnabled = false` and reload/restart config (creation attempts now correctly fail with "The External Initiator feature is disabled by configuration").
4. Using the previously captured `AccessKey`/`Secret`, send a request to an endpoint protected by `AuthenticateExternalInitiator` (e.g., a job run trigger endpoint) with the `X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers.
5. Observe that `AuthenticateExternalInitiator` in `core/web/auth/auth.go` succeeds (no flag check exists in that function), grants `UserRoleRun`, and the run is triggered — despite the feature being disabled.

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
