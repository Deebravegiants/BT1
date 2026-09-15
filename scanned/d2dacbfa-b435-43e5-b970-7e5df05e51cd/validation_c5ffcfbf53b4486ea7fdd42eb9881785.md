### Title
Unprivileged view-role users can enumerate External Initiator credentials (AccessKey/OutgoingToken) via `GET /v2/external_initiators` - ([File: core/web/router.go])

### Summary
The `GET /v2/external_initiators` route is registered with only session/token authentication and no minimum-role check, unlike the sibling `POST`/`DELETE` routes on the same resource which require `auth.RequiresEditRole`. This lets any authenticated user — including the lowest-privileged `View` role — enumerate all configured External Initiators and their credential material (`AccessKey`, `OutgoingToken`).

### Finding Description
In `v2Routes` in `core/web/router.go`, the External Initiator routes are: [1](#0-0) 

Note the asymmetry: `Create` and `Destroy` are wrapped in `auth.RequiresEditRole`, but `Index` (the list endpoint) is not wrapped in any role check at all — it only inherits the base `authv2` group's session/token authentication, meaning any authenticated node user, including one with the `View` role (the lowest role in the system, defined in `core/sessions` and enforced via `auth.RequiresEditRole`/`auth.RequiresAdminRole` at `core/web/auth/auth.go:217-253`), can call this endpoint successfully. This is corroborated by the RBAC test table which explicitly marks this route `viewOnlyAllowed: true`: [2](#0-1) 

The handler itself performs no additional authorization and returns the full resource list: [3](#0-2) 

Critically, the returned resource includes the initiator's `AccessKey` and `OutgoingToken`, which are credential material: [4](#0-3) 

`AccessKey` is the incoming credential external initiators present when triggering job runs (verified via `AuthenticateExternalInitiator` in `core/web/auth/auth.go`), and `OutgoingToken` is used to authenticate outgoing calls the node makes back to the initiator. Both are legitimate secrets tied to job-triggering/authentication flows, not merely display metadata.

This is structurally identical to the Jenkins GitHub Branch Source advisory (CVE-2017-1000087): a low-privilege, authenticated-but-unprivileged actor can enumerate valid credential identifiers/material through a listing endpoint that lacks the permission check applied to its sibling write endpoints.

### Impact Explanation
A user granted only `View` access (meant for read-only dashboards/monitoring) can retrieve `AccessKey` and `OutgoingToken` values for every External Initiator configured on the node. `AccessKey` is usable directly to authenticate as that external initiator and trigger job runs (`POST /v2/jobs/:ID/runs` via `AuthenticateExternalInitiator`), and `OutgoingToken`/`OutgoingSecret`-class values are used to interact with the external system on the node's behalf. Exposure of these to a low-privileged internal user violates the RBAC intent of separating `View` from `Edit`/`Admin` and enables unauthorized job-run triggering or impersonation of the external initiator's outgoing call authentication, a real credential/secret disclosure with a following-attack path — consistent with CWE-200 in the source advisory.

### Likelihood Explanation
Likelihood is high for any deployment that grants `View`-role API tokens/sessions to less-trusted users (a common practice for read-only monitoring/audit accounts). No special conditions are required beyond having any valid authenticated session — the endpoint is reachable with a single unauthenticated-role-elevation-free GET request.

### Recommendation
Wrap `GET /v2/external_initiators` with the same minimum-role gate used for the write operations on this resource (e.g., `auth.RequiresEditRole` or a dedicated read-role check), or strip `AccessKey`/`OutgoingToken` from the list response for callers below `Edit` role, mirroring the Jenkins fix's principle of requiring elevated permission to enumerate credential identifiers/material.

### Proof of Concept
1. Provision a node user with role `View` (or a `View`-scoped API token).
2. Authenticate and call `GET /v2/external_initiators` (optionally with `?size=`/`page` params supported by `paginatedRequest(eia.Index)`).
3. Observe the JSON:API response contains each initiator's `accessKey` and `outgoingToken` fields (per `presenters.ExternalInitiatorResource`), despite the requester lacking `Edit`/`Admin` privileges — confirmed by the RBAC test asserting `viewOnlyAllowed: true` for this route in `core/web/auth/auth_test.go:224`.

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/auth/auth_test.go (L224-226)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
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

**File:** core/web/presenters/external_initiators.go (L57-65)
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
```
