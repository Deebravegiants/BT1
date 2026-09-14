### Title
Superfluous `view`-role permission exposes External Initiator `outgoingToken`/`accessKey` credentials via `GET /v2/external_initiators` - (File: core/web/router.go, core/web/external_initiators_controller.go, core/web/presenters/external_initiators.go)

### Summary
The `GET /v2/external_initiators` route is registered without any role gate and is explicitly allowed for the lowest-privileged `view` role, letting a minimally-privileged authenticated user retrieve the `outgoingToken` credential (and `accessKey`) for every External Initiator configured on the node.

### Finding Description
Route registration applies no role wrapper to the index route, unlike sibling routes on the same controller (`Create`/`Destroy` require `RequiresEditRole`): [1](#0-0) 

The RBAC test matrix confirms this is intentional/expected behavior today — `view`-only sessions are allowed on `GET /v2/external_initiators`: [2](#0-1) 

`ExternalInitiatorsController.Index` returns `ExternalInitiatorResource`, which includes `AccessKey` and `OutgoingToken`: [3](#0-2) [4](#0-3) 

`OutgoingToken` is a randomly generated secret created alongside `OutgoingSecret` at initiator-creation time, used by the node to authenticate itself to the external initiator's webhook endpoint: [5](#0-4) 

Granting a `view`-role user (the least-privileged authenticated role, intended only for read-only dashboards per `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` gating elsewhere in the same package) unrestricted access to this bearer credential is a superfluous-permission issue analogous to the reported `snap_getEntropy` bug class: a capability (reading long-lived outbound authentication secrets) is granted to a principal that has no functional need for it, violating least privilege. Compare with the `RequiresEditRole` gate applied to `Create`/`Destroy` on the very same resource: [1](#0-0) 

### Impact Explanation
Any user provisioned with the lowest `view` role (e.g., a read-only dashboard/monitoring account) can retrieve `outgoingToken` values for all configured External Initiators. If that token is reused as a bearer/auth credential by the receiving external system to validate that a request truly originated from the Chainlink node, its disclosure to a low-privileged internal principal broadens the practical attack/credential-exposure surface beyond what the `view` role is designed to permit, even though this is not a direct remote/unauthenticated bypass.

### Likelihood Explanation
Requires an authenticated session/API token with only `view` role — which chainlink node operators may create to grant limited read-only access to less-trusted internal users or automation. No further primitives (auth bypass, injection) are required to reach the outcome; the exposure happens through the normal, documented `Index` endpoint and is confirmed as the expected behavior by the existing RBAC test table, meaning it is reachable by design rather than an incidental bug in access-control wiring.

### Recommendation
Restrict `GET /v2/external_initiators` to at least `edit` role (matching `Create`/`Destroy`) via `auth.RequiresEditRole`, or strip `outgoingToken`/`accessKey` from the `Index` response and only return them once, at creation time (as is already done for `Secret`/`OutgoingSecret` via `ExternalInitiatorAuthentication`, which is only returned from `Create`). Update `routesRolesMap` in `core/web/auth/auth_test.go` accordingly to lock in the tightened behavior.

### Proof of Concept
1. Create/authenticate as a chainlink node user with role `view` (`sessions.UserRoleView`).
2. Issue `GET /v2/external_initiators` with that session/API token.
3. Observe the JSON response includes `accessKey` and `outgoingToken` fields for each configured external initiator (per `presenters.NewExternalInitiatorResource`), even though the `view` role is not authorized to create, modify, or delete external initiators, and has no legitimate need to read these outbound authentication secrets.

Note: I could not fully verify from the indexed code how `outgoingToken`/`outgoingSecret` are consumed on the outbound call path (e.g., whether external systems actually validate `outgoingToken` as a bearer secret) since that consumer code was not located in this pass; this affects confidence on severity but not on the core finding that a `view`-role principal can read these values via an endpoint that siblings gate at `edit`.

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
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

**File:** core/bridges/external_initiator.go (L48-57)
```go
	return &ExternalInitiator{
		Name:           strings.ToLower(eir.Name),
		URL:            eir.URL,
		AccessKey:      eia.AccessKey,
		HashedSecret:   hashedSecret,
		Salt:           salt,
		OutgoingToken:  utils.NewSecret(utils.DefaultSecretSize),
		OutgoingSecret: utils.NewSecret(utils.DefaultSecretSize),
	}, nil
}
```
