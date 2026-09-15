### Title
Missing Role-Based Authorization on External Initiator Listing Endpoint - (File: core/web/router.go)

### Summary
The Jenkins Mercurial Plugin bug (CVE-2020-2306) allowed any user with the base `Overall/Read` permission to hit an unrelated HTTP endpoint and retrieve a list of configured installation names because that specific endpoint had no dedicated permission check, unlike the plugin's mutating endpoints. The chainlink node's `GET /v2/external_initiators` route shows the analogous pattern: it is reachable by any authenticated user regardless of role, while the sibling `POST`/`DELETE` routes on the same resource require `auth.RequiresEditRole`.

### Finding Description
In `core/web/router.go`, the `authv2` group is protected only by `auth.Authenticate(... AuthenticateByToken, AuthenticateBySession)`, which establishes identity but not role [1](#0-0) . Individual routes then layer role checks (`auth.RequiresAdminRole`, `auth.RequiresEditRole`, `auth.RequiresRunRole`) as needed. For external initiators:

```go
eia := ExternalInitiatorsController{app}
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
``` [2](#0-1) 

The `GET` route has no role guard, so any user authenticated with the lowest privilege role (`UserRoleView`) can call it, whereas creating/deleting an initiator correctly requires the `edit` role [3](#0-2) . `ExternalInitiatorsController.Index` returns every configured external initiator's `Name`, `URL`, `AccessKey`, `OutgoingToken`, and timestamps via `presenters.NewExternalInitiatorResource` [4](#0-3) [5](#0-4) .

This mirrors the Jenkins bug's root cause structurally: a read/list endpoint for configured integrations lacks the finer-grained permission check applied to its sibling mutating endpoints, exposing configuration metadata (`AccessKey`, `OutgoingToken`, initiator names/URLs) to any authenticated caller, not just privileged ones.

### Impact Explanation
A low-privilege authenticated node user (`view` role) can enumerate all configured external initiators, including their `AccessKey` and `OutgoingToken`. While the `HashedSecret`/incoming secret is not directly returned, exposure of `AccessKey` and `OutgoingToken` (used for outgoing webhook authentication back to the initiator) still constitutes disclosure of sensitive integration configuration to users who should not have `edit`-level visibility, and is inconsistent with the role model the rest of that resource enforces. This is a genuine authorization-boundary inconsistency (CWE-862 analog) rather than a full secret-key compromise.

### Likelihood Explanation
Any legitimate node operator who provisions a `view`-role API user (e.g., for read-only dashboards or monitoring integrations) can trivially trigger this by calling `GET /v2/external_initiators` — no special conditions or race are required, making exploitation by an authenticated low-privilege internal user straightforward.

### Recommendation
Wrap the `GET /v2/external_initiators` route with an explicit role check consistent with the sensitivity of the returned data (e.g., `auth.RequiresEditRole` or a new `RequiresViewOrHigherRoleForSensitiveFields` guard), or redact `AccessKey`/`OutgoingToken` from the `Index` response for users below `edit`/`admin` role, mirroring how `POST`/`DELETE` on the same resource are protected.

### Proof of Concept
1. Create a node API user with `UserRoleView` via `POST /v2/users` (admin-only, one-time setup).
2. Authenticate as that view-role user (session or token).
3. Issue `GET /v2/external_initiators` — the request passes `auth.Authenticate` middleware (identity check only) and reaches `ExternalInitiatorsController.Index`, returning all configured initiators' `AccessKey`, `OutgoingToken`, `Name`, and `URL`, despite the user lacking `edit` privileges required for the sibling `Create`/`Destroy` operations on the same resource.

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

**File:** core/sessions/user.go (L29-34)
```go
const (
	UserRoleAdmin UserRole = "admin"
	UserRoleEdit  UserRole = "edit"
	UserRoleRun   UserRole = "run"
	UserRoleView  UserRole = "view"
)
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

**File:** core/web/presenters/external_initiators.go (L67-77)
```go
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
