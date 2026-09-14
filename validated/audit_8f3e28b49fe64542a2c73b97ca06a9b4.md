### Title
View-role users can read External Initiator `AccessKey`/`OutgoingToken` secrets via unauthenticated-role-gated `GET /v2/external_initiators` - (File: core/web/router.go)

### Summary
The `/v2/external_initiators` listing endpoint is registered without any role guard, while every other sensitive operation on the same resource (`Create`, `Destroy`) explicitly requires `RequiresEditRole`. As a result, any authenticated Operator UI/API user — even one restricted to the lowest `view` role — can call `GET /v2/external_initiators` and receive each initiator's `AccessKey` and `OutgoingToken`, which are the credentials used to authenticate/impersonate external initiators against the node.

### Finding Description
In `v2Routes`, the external-initiator routes are wired as: [1](#0-0) 

`Create` and `Destroy` are wrapped in `auth.RequiresEditRole`, but `Index` is only inside the `authv2` group, which merely requires a valid authenticated session or token (`AuthenticateByToken`/`AuthenticateBySession`) — it does not check the user's role at all: [2](#0-1) 

Compare this to the codebase's own role-enforcement primitives, `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole`, which explicitly gate access based on `user.Role`: [3](#0-2) 

The `Index` handler itself performs no additional authorization check — it unconditionally serializes every stored `ExternalInitiator` row: [4](#0-3) 

Critically, the presenter used for this listing includes the initiator's `AccessKey` and `OutgoingToken` in the JSON response: [5](#0-4) 

This is confirmed by the existing test, which asserts the plaintext `AccessKey` and `OutgoingToken` are returned in the `Index` response body for a client with no role restriction applied: [6](#0-5) 

This mirrors the reported bug class (Tomcat CVE-2011-1088): an authorization control (`ServletSecurity`/role annotation) that is applied to sibling operations but omitted on one route, allowing a less-privileged caller to reach data/functionality intended to require a higher privilege level.

### Impact Explanation
`AccessKey`/`OutgoingToken` are credentials: `AccessKey` is the value used by inbound requests to authenticate as the external initiator (verified against `HashedSecret`, itself not returned) and `OutgoingToken` is the token the node uses when calling back out to the initiator's webhook. A `view`-role user — who is not supposed to be able to `Create`/`Destroy`/mutate initiators — can still enumerate all initiators' `AccessKey` and `OutgoingToken` values. While `AccessKey` alone (without the corresponding `Secret`) is not sufficient to authenticate inbound job-run requests, `OutgoingToken` value disclosure to a low-privilege internal user is a role/authorization inconsistency and secret-exposure issue that violates the intended least-privilege model enforced elsewhere in this exact controller.

### Likelihood Explanation
Any authenticated user with the lowest role (`view`) can trigger this by simply calling `GET /v2/external_initiators` (or the paginated variant) — no special conditions, no attacker-controlled node/gateway state needed. It is directly reachable from the standard authenticated web/API session.

### Recommendation
Add `auth.RequiresEditRole` (matching `Create`/`Destroy`) to the `GET /v2/external_initiators` route registration in `core/web/router.go`, or strip `AccessKey`/`OutgoingToken` from the `ExternalInitiatorResource` presenter used by `Index` so that only privileged callers (or dedicated single-resource endpoints) can view these secrets.

### Proof of Concept
1. Create a user with `sessions.UserRoleView`.
2. Authenticate as that user and call `GET /v2/external_initiators`.
3. Observe the response includes `accessKey` and `outgoingToken` fields for every configured external initiator, as validated by `TestExternalInitiatorsController_Index`, even though the same controller's `Create`/`Destroy` routes reject `view`-role users with `RequiresEditRole`.

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

**File:** core/web/auth/auth.go (L217-234)
```go
// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}
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
