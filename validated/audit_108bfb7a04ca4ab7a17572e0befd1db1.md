### Title
Exposure of External Initiator Secrets (AccessKey/OutgoingToken) to Any Authenticated User Regardless of Role - ([File: core/web/router.go])

### Summary
The `GET /v2/external_initiators` endpoint is registered without any minimum-role restriction (`auth.RequiresEditRole`/`auth.RequiresAdminRole`), unlike its sibling `POST`/`DELETE` routes on the same resource. Any authenticated user — including a user with the lowest `view` role — can list all configured External Initiators, and the response includes each initiator's `AccessKey` and `OutgoingToken`, which are authentication credentials used to call back into the node's job-run API.

### Finding Description
In `core/web/router.go`, the External Initiator routes are defined as: [1](#0-0) 

The `POST` and `DELETE` handlers require at least the `edit` role via `auth.RequiresEditRole`, but `GET /external_initiators` (`eia.Index`) is wrapped only in `paginatedRequest`, with no role check at all — meaning it is reachable by any user who merely passes the base `auth.Authenticate` middleware (session or token), including `UserRoleView` and `UserRoleRun`.

The handler itself performs no additional authorization and simply serializes all external initiators: [2](#0-1) 

The presenter used for serialization returns the initiator's `AccessKey` and `OutgoingToken` in full: [3](#0-2) 

These are not display-safe/redacted fields — `AccessKey` is the credential external initiators use in the `X-Chainlink-EA-AccessKey` header (paired with a `Secret` that is only returned once at creation time via `Create`), and `OutgoingToken` is the token the node sends back to the initiator's webhook. A test confirms these fields are present in the paginated `Index` response: [4](#0-3) 

This is directly analogous to the reported Syncope CVE-2018-1322 pattern: a lower-privileged, authenticated actor (there: a user with only "search" entitlement; here: a user with only "view" role) can use a listing/search endpoint to recover sensitive credential material that should require a higher privilege level, because the endpoint's authorization was not aligned with the sensitivity of the data it returns.

### Impact Explanation
Exposure of `AccessKey`/`OutgoingToken` to `view`-role users lets a low-privileged, otherwise read-only account impersonate the node when communicating with the external initiator's webhook (using `OutgoingToken`), or reuse `AccessKey` in combination with a leaked/guessed `Secret` to authenticate as the external initiator against the node's `/v2/jobs/:ID/runs` endpoint, triggering job runs (`UserRoleRun` capability) even though the account should not have been granted edit/run-level trust over integrations. This is a confidentiality break of credential material (CWE-200 analog) with a path to unauthorized job-run triggering.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment where multiple accounts with different roles exist (a common Chainlink Node Operator setup with `view` users for monitoring dashboards, etc.). No special conditions are required beyond having a valid session or API token with the `view` role — the request is a simple authenticated `GET`.

### Recommendation
Restrict `GET /v2/external_initiators` to at least `RequiresEditRole` (or `RequiresAdminRole`, matching `POST`/`DELETE`), consistent with how sensitive-credential-bearing resources should be gated. Additionally, consider not returning `OutgoingToken`/`AccessKey` in list/index responses at all — reveal them only once at creation, similar to how `Secret` is only surfaced in `NewExternalInitiatorAuthentication` at creation time.

### Proof of Concept
1. Create or obtain a Chainlink Node API user with `UserRoleView`.
2. Authenticate as that user (session cookie or API token) and issue:
   `GET /v2/external_initiators`
3. Observe the JSON:API response contains `accessKey` and `outgoingToken` for every configured External Initiator — data that a view-only account should not be able to read, confirmed by the router wiring at `core/web/router.go:264` lacking any `auth.RequiresEditRole`/`auth.RequiresAdminRole` wrapper, and by the presenter always including these fields as shown in `core/web/presenters/external_initiators.go:57-77`.

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

**File:** core/web/external_initiators_controller_test.go (L104-109)
```go
	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiBar.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiBar.Name, externalInitiators[0].Name)
	assert.Nil(t, externalInitiators[0].URL)
	assert.Equal(t, eiBar.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiBar.OutgoingToken, externalInitiators[0].OutgoingToken)
```
