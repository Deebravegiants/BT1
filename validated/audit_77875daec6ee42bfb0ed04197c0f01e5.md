I found the analog. The `GET /v2/external_initiators` endpoint at [1](#0-0) ### Title
View-role users can read the `OutgoingToken` secret for any External Initiator via `GET /v2/external_initiators` - (File: core/web/external_initiators_controller.go)

### Summary
The `GET /v2/external_initiators` endpoint returns each External Initiator's `OutgoingToken` to any authenticated user, including users with the lowest, read-only `view` role. `OutgoingToken` is a bearer secret that Chainlink itself presents to the initiator's remote webhook URL when notifying it of new jobs; its disclosure to an unprivileged/view-only session lets that user impersonate the node to the external initiator, mirroring the GitLab bug class where an export path leaked a webhook secret to an actor who should not have had it.

### Finding Description
`ExternalInitiatorsController.Index` builds a `presenters.ExternalInitiatorResource` for every stored initiator and serializes it directly to the caller: [2](#0-1) 

`ExternalInitiatorResource` (and its constructor) explicitly includes `OutgoingToken`, unredacted: [3](#0-2) 

This is not test-only behavior: the controller test asserts that `OutgoingToken` is returned verbatim in the list response: [4](#0-3) 

Critically, the route is registered with no minimum-role guard, unlike `Create`/`Destroy` on the same resource which require `RequiresEditRole`: [5](#0-4) 

The RBAC route map used by the test suite confirms `GET /v2/external_initiators` is explicitly marked `viewOnlyAllowed: true`, i.e., a `view`-role session (the lowest privilege tier, intended only for read access to non-sensitive dashboards) can call it: [6](#0-5) 

By contrast, the `OutgoingToken`/`OutgoingSecret` pair is treated as sensitive at creation time — `Create` only returns it once via `ExternalInitiatorAuthentication` at creation and gates mutating actions behind `RequiresEditRole`: [7](#0-6) 
but the same value is trivially re-obtainable afterward by any authenticated user (including `view`) via `Index`, defeating the intent of restricting initiator secrets to privileged roles.

`OutgoingToken` is used together with `OutgoingSecret` as the credential Chainlink sends to the initiator's remote URL for outbound run notifications (analogous to the webhook token in the GitLab report), so its disclosure allows a low-privilege internal actor to impersonate the Chainlink node to that external system or replay/forge outgoing-initiator calls.

### Impact Explanation
A user granted only the `view` role — meant to be read-only and non-sensitive — can enumerate all configured External Initiators and harvest every `OutgoingToken`. With that token, the low-privileged actor can impersonate the Chainlink node against the initiator's remote endpoint, potentially triggering unauthorized actions on that third-party system or intercepting/spoofing outgoing initiator traffic. This is a cross-role secret disclosure: a secret intended to be protected behind `edit`/`admin` privileges is exposed to any authenticated session.

### Likelihood Explanation
Likelihood is high for any deployment that uses the External Initiator feature and has multiple user roles configured (e.g., `view` accounts for auditors/read-only dashboards). No special conditions are required beyond having any valid session and calling a normal, paginated, documented API endpoint (`GET /v2/external_initiators`).

### Recommendation
Do not include `OutgoingToken` (or any other initiator secret) in the `ExternalInitiatorResource` returned by `Index`/`Show`-style read endpoints. If the token must be surfaced to operators, gate the listing endpoint with `auth.RequiresEditRole` (or higher) consistent with `Create`/`Destroy`, or strip the secret fields from the presenter used for listing and only reveal them once at creation, matching the pattern already used for `ExternalInitiatorAuthentication`.

### Proof of Concept
1. As an admin, create a `view`-role user session (or use an API token scoped to `view`).
2. As an `edit`/`admin` user, create an External Initiator: `POST /v2/external_initiators {"name":"foo","url":"http://example.com"}` — note the returned `outgoingToken`.
3. Authenticate as the `view`-role user and call `GET /v2/external_initiators`.
4. Observe the response includes the same `outgoingToken` value for the `foo` initiator, as demonstrated by the assertions in [8](#0-7) , confirming a `view`-privileged actor can obtain the secret without going through `RequiresEditRole`.

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

**File:** core/web/external_initiators_controller.go (L92-99)
```go
	eic.App.GetAuditLogger().Audit(audit.ExternalInitiatorCreated, map[string]any{
		"externalInitiatorID":   ei.ID,
		"externalInitiatorName": ei.Name,
		"externalInitiatorURL":  ei.URL,
	})

	resp := presenters.NewExternalInitiatorAuthentication(*ei, *eia)
	jsonAPIResponseWithStatus(c, resp, "external initiator authentication", http.StatusCreated)
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

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
```
