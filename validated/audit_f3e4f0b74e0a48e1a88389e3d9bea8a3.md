Audit Report

## Title
Missing role check on External Initiator listing endpoint discloses AccessKey/OutgoingToken to any authenticated user - (File: core/web/router.go)

## Summary
The `GET /v2/external_initiators` route is registered with only the generic `authv2` authentication group and no role-based authorization wrapper, unlike the sibling `POST`/`DELETE` routes for the same resource which are wrapped in `auth.RequiresEditRole`. This lets any authenticated user, including one with the lowest privilege role (`UserRoleView`), enumerate `AccessKey` and `OutgoingToken` values for all configured External Initiators via `ExternalInitiatorsController.Index`, which are serialized by `presenters.NewExternalInitiatorResource`.

## Finding Description
In `core/web/router.go`, the External Initiator routes are: [1](#0-0) 

The `authv2` group only requires successful authentication (`auth.AuthenticateByToken` or `auth.AuthenticateBySession`), with no minimum role: [2](#0-1) 

`Create` and `Destroy` explicitly add `auth.RequiresEditRole`, but `Index` (wrapped only in `paginatedRequest`) does not. `Index` returns all External Initiators via `presenters.NewExternalInitiatorResource`, which includes `AccessKey` and `OutgoingToken` fields: [3](#0-2) [4](#0-3) 

The system defines four ordered roles — `UserRoleAdmin`, `UserRoleEdit`, `UserRoleRun`, `UserRoleView` — confirming `view` is a valid, lower-privileged authenticated role distinct from `edit`: [5](#0-4) 

This confirms the broken assumption: mutation endpoints for this resource are gated behind `RequiresEditRole` specifically because the underlying data (`AccessKey`/`OutgoingToken`) is sensitive, but the read endpoint that discloses the same sensitive fields has no equivalent role gate, allowing a `view`-role (or `run`-role) authenticated user to read data intended to be edit-protected.

## Impact Explanation
This is an authorization-gap / secret-disclosure issue in scope as "key/secret exfiltration" and "node API authentication or role bypass": a lower-privileged authenticated principal (view/run role or an API token with matching lower role) can read `AccessKey` and `OutgoingToken` for every External Initiator configured on the node, data explicitly intended to be edit-role protected per the `Create`/`Destroy` gating. This could enable impersonation of the External Initiator's outbound token flow or facilitate further attacks using the leaked access key material, undermining the node's internal role-separation model for a credential-bearing resource.

## Likelihood Explanation
Any authenticated user or API token holder, regardless of assigned role, can issue `GET /v2/external_initiators` since the route enforces only authentication, not authorization — no special conditions, elevated access, or misconfiguration are required. This is a straightforward, repeatable read-only HTTP request against the standard node API.

## Recommendation
Wrap the `GET /v2/external_initiators` route with a role check consistent with the mutation endpoints, e.g. `auth.RequiresEditRole(eia.Index)` (or `RequiresRunRole` at minimum), matching the protection already applied to `Create`/`Destroy`. Additionally, consider removing `AccessKey`/`OutgoingToken` from `ExternalInitiatorResource` list responses entirely, mirroring how `Secret`/`OutgoingSecret` are already excluded from that struct.

## Proof of Concept
1. Create two node users: one with `UserRoleView` (or `UserRoleRun`) and one with `UserRoleAdmin`/`UserRoleEdit` used to create an External Initiator via `POST /v2/external_initiators` (protected by `RequiresEditRole`).
2. Authenticate as the low-privileged `view`/`run` user (session cookie or API token).
3. Issue `GET /v2/external_initiators`.
4. Observe the JSON response includes `accessKey` and `outgoingToken` fields for the External Initiator created in step 1, per `ExternalInitiatorResource` in `core/web/presenters/external_initiators.go`, despite the same low-privileged user being rejected (403) if it attempted `POST`/`DELETE` on `/v2/external_initiators` due to `auth.RequiresEditRole`.
5. A Go handler/integration test analogous to `core/web/external_initiators_controller_test.go` asserting that a `view`-role authenticated client receives a 200 with `accessKey`/`outgoingToken` populated would confirm the gap.

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

**File:** core/sessions/user.go (L29-34)
```go
const (
	UserRoleAdmin UserRole = "admin"
	UserRoleEdit  UserRole = "edit"
	UserRoleRun   UserRole = "run"
	UserRoleView  UserRole = "view"
)
```
