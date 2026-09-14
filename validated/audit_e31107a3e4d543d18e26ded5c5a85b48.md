### Title
GET /v2/external_initiators exposes OutgoingToken/AccessKey credentials to view-only users due to missing role gate - ([File: core/web/router.go])

### Summary
The docker-socket-proxy CVE describes a class of bug where a read-only GET endpoint is not gated with the same access-control granularity as its write counterparts, letting an actor with minimal privilege pull sensitive data through the "read" path. Chainlink's `/v2/external_initiators` index route exhibits the same structural flaw: it is registered without any role-requiring middleware while its sibling write routes on the same resource are explicitly wrapped with `auth.RequiresEditRole`.

### Finding Description
In `core/web/router.go`, the `external_initiators` routes are declared as: [1](#0-0) 

```go
eia := ExternalInitiatorsController{app}
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

`POST` and `DELETE` require at least the `edit` role, but `GET` only requires the base `Authenticate` middleware applied to the whole `/v2` group (`auth.AuthenticateByToken` / `auth.AuthenticateBySession`), which lets any authenticated user, including `UserRoleView`, hit the handler [2](#0-1) .

`ExternalInitiatorsController.Index` returns the full `ExternalInitiatorResource` for every stored external initiator, including `OutgoingToken`, the credential the node itself uses to authenticate outbound webhook calls to external initiator services: [3](#0-2) [4](#0-3) 

The RBAC test suite confirms this behavior is intentional/expected as-is: `viewOnlyAllowed=true` for `GET /v2/external_initiators`, unlike its write siblings which are `false` for view-only: [5](#0-4) 

This matches the CVE pattern: read-only verbs on a resource are insufficiently gated relative to write verbs, and the read path leaks data that should be protected at a higher privilege tier — here `OutgoingToken`, a secret used for request authentication/impersonation of the node's outbound calls, is exposed to a role (`view`) that has no legitimate need to manage external initiators.

### Impact Explanation
A user provisioned with only the `view` role (the lowest privilege tier, intended for read-only dashboard access) can retrieve `OutgoingToken` for every configured external initiator via a simple `GET /v2/external_initiators` call. `OutgoingToken` is the credential the chainlink node sends to prove its identity to the external initiator's webhook endpoint. Disclosure of this token to an unprivileged internal user allows that user to impersonate the node to the external initiator system, a concrete instance of request/credential impersonation enabled purely by a role-check gap on a read endpoint, not by any application logic bug in the initiator flow itself.

### Likelihood Explanation
Likelihood is moderate: exploitation requires only a valid `view`-role session or API token (the lowest privilege class explicitly supported by chainlink's RBAC and OIDC/LDAP role mapping — see `sessions.UserRoleView`), and a single unauthenticated-by-role GET request. No additional conditions, chains, or race windows are needed; the RBAC test harness itself documents that this route intentionally allows view-only access, confirming the gap is reachable and reproducible in normal operation.

### Recommendation
Wrap `GET /v2/external_initiators` (and `Show`, if added later) with a role check consistent with the sensitivity of `OutgoingToken`/`AccessKey`, e.g. `auth.RequiresEditRole` (matching `Create`/`Destroy`), or strip `OutgoingToken`/`AccessKey`/`OutgoingSecret` from `ExternalInitiatorResource` for view-level GETs and only return them from the one-time `Create` response (`ExternalInitiatorAuthentication`) as is already done for the initial creation flow.

### Proof of Concept
1. Provision a chainlink API user with `UserRoleView` (minimal internal privilege).
2. As an admin/edit user, create an external initiator via `POST /v2/external_initiators` — note the response only returns secrets once (`presenters.ExternalInitiatorAuthentication`).
3. Authenticate as the `view`-role user and call `GET /v2/external_initiators`.
4. Observe the response includes `outgoingToken` (and `accessKey`) for the initiator created in step 2, despite the requesting user having only view privileges — confirmed by the RBAC test expecting `viewOnlyAllowed=true` and no `http.StatusForbidden`/`http.StatusUnauthorized` for this route [6](#0-5) .

### Citations

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

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

**File:** core/web/auth/auth_test.go (L224-226)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
```
