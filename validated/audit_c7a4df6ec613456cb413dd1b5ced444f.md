### Title
Unprivileged authenticated users (view role) can enumerate External Initiator `AccessKey` and `OutgoingToken` via `GET /v2/external_initiators` - (File: core/web/external_initiators_controller.go)

### Summary
The Jenkins GitLab Plugin advisory (CVE-2022-30955) describes an endpoint that let low-privileged (`Overall/Read`) users enumerate credential IDs due to a missing permission check. The analogous pattern in this codebase is the `Index` handler for external initiators, which is reachable by any authenticated user regardless of role (including the lowest `view` role) and returns each external initiator's `AccessKey` and `OutgoingToken` values.

### Finding Description
`ExternalInitiatorsController.Index` queries all external initiators and serializes them with `presenters.NewExternalInitiatorResource`, which includes the `AccessKey` and `OutgoingToken` fields in the JSON response: [1](#0-0) [2](#0-1) 

The route is registered without any role-based middleware beyond generic authentication (`paginatedRequest(eia.Index)`, no `auth.RequiresEditRole`/`RequiresAdminRole` wrapper), unlike the `Create` and `Destroy` routes on the same resource, which are wrapped with `auth.RequiresEditRole`: [3](#0-2) 

The test suite's own RBAC route map confirms `GET /v2/external_initiators` is `viewOnlyAllowed: true`, i.e., accessible to the lowest privilege tier: [4](#0-3) 

`AccessKey` and `Secret` (via `auth.Token`) are the credential pair used by `AuthenticateExternalInitiator` to authorize inbound webhook calls that trigger job runs with an implicit `run` role: [5](#0-4) 

While the response does not include the `Secret` field (present only in `ExternalInitiatorAuthentication`, returned only at creation time), it does expose `AccessKey` (the credential identifier used to look up the initiator, analogous to the "credentials IDs" enumerated in the Jenkins advisory) and `OutgoingToken` (used to authenticate outgoing calls to the external initiator's URL) to any authenticated view-only user.

### Impact Explanation
A user provisioned with only the `view` role (the lowest privilege level intended for read-only dashboards) can retrieve the `AccessKey` and `OutgoingToken` of every external initiator configured on the node. This is a credential/token enumeration exposure consistent with CWE-862 (Missing Authorization) — impact is limited to confidentiality of these secondary identifiers/tokens (`OutgoingToken` in particular could be used to impersonate the node when calling back to the external initiator's endpoint, or to correlate/target the `AccessKey` for further attack), matching the "Low confidentiality impact" characterization of the referenced advisory.

### Likelihood Explanation
Likelihood is high for any deployment that provisions `view`-role API users or OIDC/LDAP `ReadClaim`/`ReadUserGroupCN` roles for third parties (dashboards, monitoring, auditors) — a common and documented configuration: [6](#0-5) 
Exploitation requires no more than a valid low-privilege session/API token and a single unauthenticated-by-role `GET` request; no additional discovery or complex conditions are needed.

### Recommendation
Restrict `GET /v2/external_initiators` (and `GET /v2/external_initiators/:id` if applicable) with `auth.RequiresEditRole` or `auth.RequiresAdminRole`, consistent with how `Create`/`Destroy` are protected, or strip `AccessKey`/`OutgoingToken` from `ExternalInitiatorResource` for non-privileged roles.

### Proof of Concept
1. Provision a Chainlink node user with role `view` (or configure OIDC `ReadClaim`/LDAP `ReadUserGroupCN` mapping).
2. Authenticate as that user (session cookie or API token).
3. Send `GET /v2/external_initiators` with the low-privilege session/token.
4. Observe the JSON response containing `accessKey` and `outgoingToken` for every configured external initiator, confirmed by the route being explicitly marked `viewOnlyAllowed: true` in the RBAC test matrix: [7](#0-6) 

---
**Confidence caveat:** I could not fully verify from the index whether `OutgoingToken` alone (without `OutgoingSecret`) is sufficient to impersonate calls to the external initiator endpoint, since `OutgoingSecret` usage in `bridges/external_initiator.go` was not fully inspected in this session. The severity assessment (confidentiality-only, no direct auth bypass since `Secret`/`OutgoingSecret` are withheld) should be validated against `core/bridges/external_initiator.go` before treating this as equivalent-severity to the original CVE.

### Citations

**File:** core/web/external_initiators_controller.go (L50-59)
```go
func (eic *ExternalInitiatorsController) Index(c *gin.Context, size, page, offset int) {
	ctx := c.Request.Context()
	externalInitiators, count, err := eic.App.BridgeORM().ExternalInitiators(ctx, offset, size)
	resources := make([]presenters.ExternalInitiatorResource, 0, len(externalInitiators))
	for _, initiator := range externalInitiators {
		resources = append(resources, presenters.NewExternalInitiatorResource(initiator))
	}

	paginatedResponse(c, "externalInitiators", size, page, resources, count, err)
}
```

**File:** core/web/presenters/external_initiators.go (L57-77)
```go
type ExternalInitiatorResource struct {
	JAID
	Name          string         `json:"name"`
	URL           *models.WebURL `json:"url"`
	AccessKey     string         `json:"accessKey"`
	OutgoingToken string         `json:"outgoingToken"`
	CreatedAt     time.Time      `json:"createdAt"`
	UpdatedAt     time.Time      `json:"updatedAt"`
}

func NewExternalInitiatorResource(ei bridges.ExternalInitiator) ExternalInitiatorResource {
	return ExternalInitiatorResource{
		JAID:          NewJAID(strconv.FormatInt(ei.ID, 10)),
		Name:          ei.Name,
		URL:           ei.URL,
		AccessKey:     ei.AccessKey,
		OutgoingToken: ei.OutgoingToken,
		CreatedAt:     ei.CreatedAt,
		UpdatedAt:     ei.UpdatedAt,
	}
}
```

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/auth/auth_test.go (L215-226)
```go
	{"GET", "/v2/users", false, false, false},
	{"POST", "/v2/users", false, false, false},
	{"PATCH", "/v2/users", false, false, false},
	{"DELETE", "/v2/users/MOCK", false, false, false},
	{"PATCH", "/v2/user/password", true, true, true},
	{"POST", "/v2/user/token", true, true, true},
	{"POST", "/v2/user/token/delete", true, true, true},
	{"GET", "/v2/enroll_webauthn", true, true, true},
	{"POST", "/v2/enroll_webauthn", true, true, true},
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
```

**File:** core/web/auth/auth.go (L119-148)
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
```

**File:** core/config/docs/core.toml (L224-227)
```text
# RunClaim is string label of the id claim that maps the core node's 'Run' role
RunClaim = 'NodeRunners' # Default
# ReadClaim is string label of the id claim that maps the core node's 'Read' role
ReadClaim = 'NodeReadOnly' # Default
```
