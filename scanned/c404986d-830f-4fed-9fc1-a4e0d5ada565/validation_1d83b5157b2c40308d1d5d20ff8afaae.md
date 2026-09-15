### Title
Unprivileged (View-role) users can enumerate `OutgoingToken` and `AccessKey` credentials for all External Initiators - (File: core/web/router.go, core/web/external_initiators_controller.go)

### Summary
The `GET /v2/external_initiators` endpoint returns `AccessKey` and `OutgoingToken` for every External Initiator registered on the node, but the route is protected only by session/token authentication — it is not gated behind `auth.RequiresEditRole` (or any elevated role), unlike the sibling `Create`/`Destroy` routes for the same resource. Any authenticated user, including one with the lowest privilege level (`UserRoleView`), can read these values.

### Finding Description
This is the same bug *class* as ALPINE-CVE-2021-28544 (Subversion revealing an authz-protected `copyfrom` path to a user who should not see it): a piece of metadata that is meant to be restricted to privileged operations leaks through a read path that has weaker authorization than the corresponding write/management path.

In `core/web/router.go`, the routes for external initiators are: [1](#0-0) 

```go
eia := ExternalInitiatorsController{app}
authv2.GET("/external_initiators", paginatedRequest(eia.Index))
authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

`Create` and `Destroy` require the `Edit` role, but `Index` (the listing/read endpoint) has no role guard at all — it inherits only the generic `authv2` session/token authentication middleware, which any logged-in user (including `UserRoleView`) satisfies: [2](#0-1) 

`ExternalInitiatorsController.Index` fetches every stored `ExternalInitiator` and serializes it via `presenters.NewExternalInitiatorResource`, which is returned to the caller: [3](#0-2) 

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

The presenter includes both the `AccessKey` (identity/username-equivalent credential for the initiator) and the `OutgoingToken` (a secret used by Chainlink to authenticate outbound webhook/job-run-trigger callbacks to the initiator): [4](#0-3) 

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

This is confirmed by an existing test that reads `AccessKey`/`OutgoingToken` straight off the unauthenticated-by-role `Index` response: [5](#0-4) 

Note: the `IncomingToken`/`Secret` (used to authenticate *inbound* requests from the initiator to Chainlink) is not present in `ExternalInitiatorResource`, only `AccessKey` and `OutgoingToken`. So this is not a full request-forgery primitive, but it is still a straightforward "protected metadata revealed to an under-privileged actor" bug matching the CVE's bug class: the read path exposes data (`AccessKey`, `OutgoingToken`) that the design otherwise treats as privileged (only Edit-role users may create/destroy initiators and thus should be the only ones expected to handle these values).

### Impact Explanation
A user with only `View` role (the lowest role in the node's RBAC model — `UserRoleView`/`NodeReadOnly`) can call `GET /v2/external_initiators` and learn every registered initiator's `AccessKey` and `OutgoingToken`. `AccessKey` is effectively the initiator identity; combined with knowledge of the URL and naming conventions, this weakens the security boundary between roles that the rest of the External-Initiator API enforces (Create/Destroy require Edit). This is a role-boundary/information-disclosure issue rather than a full account-takeover, since the `IncomingToken`/hashed secret used for *inbound* authentication is not exposed here.

### Likelihood Explanation
High: exploitation requires nothing beyond a valid low-privilege (`View`) session or API token on the node's web/API server — a routine and expected access level for many operators, dashboards, or read-only integrations. No race condition, timing, or special network position is needed; it's a single unauthenticated-by-role GET request.

### Recommendation
Wrap the `GET /v2/external_initiators` route with the same (or stricter) role requirement used for mutation of the resource, e.g. `auth.RequiresEditRole(paginatedRequest(eia.Index))`, or scrub `AccessKey`/`OutgoingToken` from the `ExternalInitiatorResource` returned to non-privileged roles.

### Proof of Concept
1. Create a Chainlink node user with role `view`.
2. As an `admin`/`edit` user, register an external initiator: `POST /v2/external_initiators` with `{"name":"victim-initiator"}` — note the returned `outgoingToken`.
3. Log in as the `view` user and call `GET /v2/external_initiators`.
4. Observe the response contains `accessKey` and `outgoingToken` for `victim-initiator`, identical to what only an `edit`/`admin` user should be able to obtain, despite `view` never being granted access to create/manage initiators.

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
```

**File:** core/web/auth/auth.go (L215-234)
```go
}

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
