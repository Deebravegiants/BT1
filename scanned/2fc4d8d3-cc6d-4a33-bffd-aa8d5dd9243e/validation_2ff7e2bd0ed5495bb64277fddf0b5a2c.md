### Title
View-only users can read External Initiator credentials via `GET /v2/external_initiators` - (File: `core/web/external_initiators_controller.go`)

### Summary
The `/v2/external_initiators` listing endpoint is reachable by any authenticated node API user, including the lowest-privilege `view` role, and returns each External Initiator's `AccessKey` and `OutgoingToken` credential material. These fields are meant to gate which external systems may trigger job runs and which token the node uses when calling back out to the external initiator, so exposing them to a role that should have read-only, non-sensitive visibility is an authorization/information-disclosure gap analogous to the GitLab CVE-2021-39905 pattern, where an under-privileged actor could see data that should have been scoped to a more privileged relationship.

### Finding Description
The route is registered without any role guard: [1](#0-0) 
so `auth.RequiresEditRole`/`auth.RequiresRunRole` is applied only to `Create`/`Destroy`, not to `Index`. Any authenticated session (session cookie or API token), regardless of role, reaches `ExternalInitiatorsController.Index`: [2](#0-1) 
This handler serializes every stored `bridges.ExternalInitiator` via `presenters.NewExternalInitiatorResource`, which includes the `AccessKey` and `OutgoingToken` fields directly in the JSON:API response: [3](#0-2) 
The route-role test matrix confirms this endpoint is explicitly allowed for `view`-role sessions (`viewOnlyAllowed: true`) alongside `run` and `edit`: [4](#0-3) 
By contrast, sibling mutating routes (`POST`/`DELETE` on the same resource) correctly require `edit` role: [5](#0-4) 
This mirrors the GitLab bug class: the read path for a resource that carries sensitive relationship/credential metadata is not scoped to the privilege level appropriate for that data, allowing a lesser-privileged authenticated actor to view information intended for higher-trust roles.

### Impact Explanation
`AccessKey` is the identifier External Initiator clients present (paired with a `Secret`, never returned again after creation) to authenticate inbound run-trigger requests via `AuthenticateExternalInitiator`: [6](#0-5) 
`OutgoingToken`/`OutgoingSecret` are the credentials chainlink uses to call back out to the initiator. Disclosure of `AccessKey`/`OutgoingToken` to a `view`-role user (who under the RBAC model should not have edit/run-level operational visibility) leaks operational integration metadata that helps profile which external systems can trigger runs, and, combined with any other secret-recovery vector, could facilitate impersonation of the initiator's outgoing calls. This is a confidentiality/authorization-boundary issue rather than a direct fund-loss or full auth bypass, since the `Secret` itself is not returned in `Index`.

### Likelihood Explanation
Any user issued a `view`-role API token or session (a legitimate, low-trust account) can trigger this with a single unauthenticated-role-check `GET /v2/external_initiators` call; no special conditions are required, and the routes/table above prove reachability is intentional per the test suite rather than accidental.

### Recommendation
Wrap `ExternalInitiatorsController.Index` with `auth.RequiresEditRole` (or at minimum `RequiresRunRole`) matching the `Create`/`Destroy` handlers, and strip `AccessKey`/`OutgoingToken` from the resource returned to roles that don't need them, consistent with how `Secret`/`OutgoingSecret` are already excluded from `ExternalInitiatorResource`.

### Proof of Concept
1. Create a user with `view` role and issue an API token via the admin CLI.
2. Using that token's `X-API-KEY`/`X-API-SECRET` headers, call `GET /v2/external_initiators`.
3. Observe the response contains each initiator's `accessKey` and `outgoingToken`, despite the requester holding only the `view` role, which per `routesRolesMap` in `auth_test.go` is explicitly asserted as allowed.

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

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

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
```

**File:** core/web/auth/auth_test.go (L225-226)
```go
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
```

**File:** core/web/auth/auth.go (L119-146)
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
```
