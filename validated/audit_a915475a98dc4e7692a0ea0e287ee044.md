All the claim's technical assertions check out against the actual source.All claims are confirmed by direct inspection of the source: the `GET /v2/external_initiators` route has no role guard (unlike `POST`/`DELETE` on the same resource), the `Index` handler serializes `AccessKey` and `OutgoingToken` in the JSON response, and the test suite (`auth_test.go`) explicitly documents this endpoint as `viewOnlyAllowed: true`. This is a genuine, code-verified authorization gap where credential material is exposed to the lowest-privilege role.

Audit Report

## Title
View-only users can read External Initiator credentials via `GET /v2/external_initiators` - (File: `core/web/external_initiators_controller.go`)

## Summary
The `GET /v2/external_initiators` endpoint has no role restriction, unlike its sibling `POST`/`DELETE` routes which require `edit` role. Any authenticated user with only `view`-role credentials can call this endpoint and receive each External Initiator's `AccessKey` and `OutgoingToken` in the response body.

## Finding Description
In `core/web/router.go`, the route is registered as `authv2.GET("/external_initiators", paginatedRequest(eia.Index))` with no `auth.RequiresEditRole`/`auth.RequiresRunRole` wrapper, while `POST` and `DELETE` on the same path are wrapped with `auth.RequiresEditRole`. [1](#0-0) 

The `Index` handler in `core/web/external_initiators_controller.go` fetches all `bridges.ExternalInitiator` records and serializes them via `presenters.NewExternalInitiatorResource` without any role-based filtering. [2](#0-1) 

`ExternalInitiatorResource` (used only for the read/list path) directly includes `AccessKey` and `OutgoingToken` fields, whereas `ExternalInitiatorAuthentication` (used only for the one-time `Create` response) correctly separates `Secret`/`OutgoingSecret` from being returned again — but `Index` still leaks the paired `AccessKey`/`OutgoingToken`. [3](#0-2) 

The RBAC test matrix in `core/web/auth/auth_test.go` confirms this is intentional/tested behavior: `GET /v2/external_initiators` is marked `viewOnlyAllowed: true`, while `POST`/`DELETE` on the same resource are marked `false, false, true` (edit-only). [4](#0-3) 

## Impact Explanation
`AccessKey` is the credential presented by external initiator clients to authenticate inbound run-trigger requests, and `OutgoingToken` is used by the node when calling back out to the initiator. Disclosing this material to a `view`-role account (the lowest-privilege authenticated role, intended for read-only, non-sensitive visibility) leaks operational integration credentials that should be scoped to `edit`/`run`-level trust. This maps to an in-scope "key/secret exfiltration" impact category, though the blast radius is bounded since the paired `Secret` itself is never returned by `Index`.

## Likelihood Explanation
Any user provisioned with a `view`-role API token or session can trigger this with a single `GET /v2/external_initiators` request — no special conditions, race, or additional vulnerability chain required. The behavior is deterministic and explicitly encoded/asserted in the existing test suite as allowed for view-only users, confirming it's the current (likely unintended) production behavior rather than a hypothetical.

## Recommendation
Wrap `ExternalInitiatorsController.Index` with `auth.RequiresEditRole` (or `auth.RequiresRunRole` at minimum) to match the `Create`/`Destroy` handlers on the same resource. Additionally, consider excluding `AccessKey`/`OutgoingToken` from `ExternalInitiatorResource` entirely, or introducing a reduced view-role-safe resource that omits credential fields, consistent with how `Secret`/`OutgoingSecret` are excluded from repeat exposure elsewhere.

## Proof of Concept
1. Provision a user account with `view` role only, and issue an API token for that user via the admin CLI/API.
2. With that token's headers, issue `GET /v2/external_initiators` against a running node.
3. Observe the JSON:API response includes `accessKey` and `outgoingToken` for every stored external initiator, as returned by `NewExternalInitiatorResource` in `core/web/presenters/external_initiators.go`. This can also be verified as a Go test by extending `core/web/auth/auth_test.go`'s existing table-driven RBAC test (which already asserts `viewOnlyAllowed: true` for this route) with an assertion on response body field presence, or by adding an integration test in `core/web/external_initiators_controller_test.go` using a view-role session/token.

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

**File:** core/web/auth/auth_test.go (L224-226)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
```
