### Title
Missing role-based authorization on `GET /v2/external_initiators` exposes External Initiator credentials to any authenticated user - ([File: core/web/router.go])

### Summary
The `/v2/external_initiators` listing endpoint is registered without any minimum-role authorization middleware, unlike every other mutating or credential-adjacent route on the same resource. Any authenticated user — including the lowest-privilege `view` role — can enumerate all configured External Initiators and retrieve their `AccessKey` and `OutgoingToken` values.

### Finding Description
In `core/web/router.go`, the `External Initiators` routes are registered as:
```go
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
``` [1](#0-0) 

`Create` and `Destroy` are gated by `auth.RequiresEditRole`, which rejects `view` and `run` role sessions, but `Index` has no role gate at all — it only sits behind the generic `authv2` group, which merely requires *any* successful session or token authentication:
```go
authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
    auth.AuthenticateByToken,
    auth.AuthenticateBySession,
))
``` [2](#0-1) 

`ExternalInitiatorsController.Index` returns every stored initiator's `AccessKey` and `OutgoingToken` via `presenters.ExternalInitiatorResource`, with no additional per-caller filtering or redaction:
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
``` [3](#0-2) 
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
``` [4](#0-3) 

This is confirmed by the existing test, which asserts a plain (role-less) authenticated client can list initiators and receive their `AccessKey`/`OutgoingToken`:
```go
client := app.NewHTTPClient(nil)
...
resp, cleanup = client.Get("/v2/external_initiators?size=1")
...
assert.Equal(t, eiBar.AccessKey, externalInitiators[0].AccessKey)
assert.Equal(t, eiBar.OutgoingToken, externalInitiators[0].OutgoingToken)
``` [5](#0-4) 

The reachable path is: unprivileged client → `AuthenticateBySession`/`AuthenticateByToken` (only proves *some* valid account, any role) → `Index` handler → full credential dump, with **no caller-authorization/role check** analogous to the sibling `Create`/`Destroy` routes on the very same resource. This mirrors the report's bug class: a permission mechanism exists in the codebase (role-based route gating) but is skipped for this particular entry point, letting a caller with the lowest privilege level reach data that should require the `edit`/`admin` role that guards every other operation on this resource.

### Impact Explanation
`AccessKey` and `OutgoingToken` are per-initiator operational secrets: `AccessKey` is one half of the credential pair (`X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret`) used to authenticate inbound webhook job-run triggers, and `OutgoingToken` is used by the node to authenticate its own outbound calls back to the External Initiator service. A low-privilege `view`-role user (e.g., an operator granted only read access for dashboards) can harvest these values for every configured initiator across the node, undermining the intended role segregation and aiding further impersonation/reconnaissance against downstream External Initiator services.

### Likelihood Explanation
High: the endpoint is reachable by any account that can authenticate at all (including the minimum `view` role), requires no special conditions, and the disclosure is deterministic and unconditional — every call returns the full credential set for all initiators, as directly demonstrated by the existing unit test.

### Recommendation
Add `auth.RequiresEditRole` (or an equivalent minimum-role guard) to the `GET /v2/external_initiators` route to match the authorization level enforced on `Create`/`Destroy`, or strip `AccessKey`/`OutgoingToken` from the `Index` response for callers below `edit` role.

### Proof of Concept
1. Create a Chainlink node user with role `view` (the lowest role, normally restricted from mutating External Initiators).
2. Authenticate as this user via `/sessions` or an API token.
3. Call `GET /v2/external_initiators` — the response succeeds (no 401/403) and returns the JSON list including `accessKey` and `outgoingToken` for every configured External Initiator, exactly as asserted in `TestExternalInitiatorsController_Index` at [6](#0-5) , despite `Create`/`Destroy` on the same resource being blocked for this role by `auth.RequiresEditRole`.

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

**File:** core/web/external_initiators_controller_test.go (L72-109)
```go
	client := app.NewHTTPClient(nil)

	db := app.GetDB()
	borm := bridges.NewORM(db)

	eiFoo := cltest.MustInsertExternalInitiatorWithOpts(t, borm, cltest.ExternalInitiatorOpts{
		NamePrefix:    "foo",
		URL:           cltest.MustWebURL(t, "http://example.com/foo"),
		OutgoingToken: "outgoing_token",
	})
	eiBar := cltest.MustInsertExternalInitiatorWithOpts(t, borm, cltest.ExternalInitiatorOpts{NamePrefix: "bar"})

	resp, cleanup := client.Get("/v2/external_initiators?size=x")
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusUnprocessableEntity)

	resp, cleanup = client.Get("/v2/external_initiators?size=1")
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusOK)
	body := cltest.ParseResponseBody(t, resp)

	metaCount, err := cltest.ParseJSONAPIResponseMetaCount(body)
	require.NoError(t, err)
	require.Equal(t, 2, metaCount)

	var links jsonapi.Links
	var externalInitiators []presenters.ExternalInitiatorResource
	err = web.ParsePaginatedResponse(body, &externalInitiators, &links)
	require.NoError(t, err)
	assert.NotEmpty(t, links["next"].Href)
	assert.Empty(t, links["prev"].Href)

	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiBar.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiBar.Name, externalInitiators[0].Name)
	assert.Nil(t, externalInitiators[0].URL)
	assert.Equal(t, eiBar.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiBar.OutgoingToken, externalInitiators[0].OutgoingToken)
```
