All claims are confirmed by the actual code. The `GET /v2/external_initiators` route is registered with only base authentication (no `RequiresEditRole`/`RequiresAdminRole` wrapper), unlike the sibling `Create`/`Destroy` routes on the same resource.All findings in the report are verified against the actual code. This is a genuine, reachable vulnerability.

Audit Report

## Title
Unprivileged "View" role can read outgoing secret tokens for External Initiators via `GET /v2/external_initiators` - (File: core/web/external_initiators_controller.go)

## Summary
The `GET /v2/external_initiators` route is registered with only base session/token authentication and no role-gating, unlike its sibling `Create`/`Destroy` routes which require `auth.RequiresEditRole`. The `Index` handler serializes each external initiator through `presenters.NewExternalInitiatorResource`, which includes the plaintext `OutgoingToken` field in the JSON response, allowing any authenticated user — including the lowest-privilege `UserRoleView` role — to read this secret credential.

## Finding Description
The route registration in `core/web/router.go` shows the asymmetry directly: `authv2.GET("/external_initiators", paginatedRequest(eia.Index))` has no role wrapper, while `authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))` and the `DELETE` route both require edit role. [1](#0-0) 

The `Index` handler in `core/web/external_initiators_controller.go` fetches all external initiators and maps each into an `ExternalInitiatorResource` via `presenters.NewExternalInitiatorResource(initiator)`, with no field redaction before returning them in the paginated response. [2](#0-1) 

The `ExternalInitiatorResource` struct in `core/web/presenters/external_initiators.go` explicitly includes `OutgoingToken string `json:"outgoingToken"`` as a non-omitted field, and `NewExternalInitiatorResource` populates it directly from the stored `ei.OutgoingToken`. [3](#0-2) 

This is corroborated by the RBAC test matrix in `core/web/auth/auth_test.go`, which explicitly documents `{"GET", "/v2/external_initiators", true, true, true}` — i.e., `viewOnlyAllowed: true` — contrasted with the `POST`/`DELETE` rows for the same resource marked `false, false, true` (edit/admin only). [4](#0-3) 

The integration test confirms the actual response body includes `OutgoingToken` in plaintext for listed initiators. [5](#0-4) 

## Impact Explanation
`OutgoingToken` is the secret credential the Chainlink node uses to authenticate its outbound webhook calls to the external initiator's service. Disclosing it to a View-role account — a role intended for read-only, non-administrative access — allows that lower-privileged actor to impersonate the node's outbound requests to the external initiator endpoint, an in-scope secret exfiltration / request impersonation impact across a privilege boundary.

## Likelihood Explanation
Exploitation requires only a valid session or API token for a user provisioned with the standard `UserRoleView` role and calling a single GET endpoint — no elevated privileges, no misconfiguration, and no additional preconditions beyond having at least one External Initiator configured (a supported, documented feature). This is trivially repeatable in any deployment that uses tiered RBAC roles and External Initiators.

## Recommendation
Gate `GET /v2/external_initiators` (and any per-ID show endpoint) behind at least `auth.RequiresEditRole`, matching the `Create`/`Destroy` routes, or strip `OutgoingToken`/`OutgoingSecret` from `ExternalInitiatorResource` used by `Index`, exposing the secret only once at creation time via the existing `ExternalInitiatorAuthentication` presenter used by `Create`.

## Proof of Concept
1. As an admin, create a user with `UserRoleView` and obtain a session cookie or API token.
2. As an admin, create an External Initiator via `POST /v2/external_initiators {"name":"foo","url":"http://example.com"}`; note the one-time `outgoingToken` in the response.
3. Authenticate as the View-role user and issue `GET /v2/external_initiators`.
4. Observe the response returns `200 OK` (not `401`/`403`) with `outgoingToken` populated for each initiator, as confirmed by the assertions in `core/web/external_initiators_controller_test.go` lines 104-126, and as predicted by the `viewOnlyAllowed: true` entry in `core/web/auth/auth_test.go` line 224.

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

**File:** core/web/external_initiators_controller_test.go (L104-126)
```go
	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiBar.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiBar.Name, externalInitiators[0].Name)
	assert.Nil(t, externalInitiators[0].URL)
	assert.Equal(t, eiBar.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiBar.OutgoingToken, externalInitiators[0].OutgoingToken)

	resp, cleanup = client.Get(links["next"].Href)
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusOK)

	externalInitiators = []presenters.ExternalInitiatorResource{}
	err = web.ParsePaginatedResponse(cltest.ParseResponseBody(t, resp), &externalInitiators, &links)
	require.NoError(t, err)
	assert.Empty(t, links["next"])
	assert.NotEmpty(t, links["prev"])

	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiFoo.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiFoo.Name, externalInitiators[0].Name)
	assert.Equal(t, eiFoo.URL.String(), externalInitiators[0].URL.String())
	assert.Equal(t, eiFoo.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiFoo.OutgoingToken, externalInitiators[0].OutgoingToken)
```
