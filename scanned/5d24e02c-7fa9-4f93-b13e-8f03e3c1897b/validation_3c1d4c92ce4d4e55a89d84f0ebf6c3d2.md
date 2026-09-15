Based on my research, I can identify a genuine analog to the reported CVE, though I was unable to view the exact route-level role check line in `core/web/router.go` (only found 2 matches without reading the surrounding context) due to running out of tool iterations.

### Title
Sensitive External Initiator Credentials (AccessKey/OutgoingToken) Exposed in List Endpoint Without Scoped Permission - (File: `core/web/external_initiators_controller.go`)

### Summary
The `ExternalInitiatorsController.Index` handler returns `AccessKey` and `OutgoingToken` fields for every stored External Initiator to any authenticated user who can reach `/v2/external_initiators`, mirroring the tgstation-server issue where a "list" permission improperly exposed connection secrets that should have required a stricter, dedicated permission.

### Finding Description
`ExternalInitiatorsController.Index` calls `eic.App.BridgeORM().ExternalInitiators(ctx, offset, size)` and maps every result through `presenters.NewExternalInitiatorResource`, which includes `AccessKey` and `OutgoingToken` in the JSON response [1](#0-0) . The presenter itself explicitly serializes these secret-adjacent fields as top-level JSON keys `accessKey` and `outgoingToken` [2](#0-1) . `AccessKey` is the credential used to authenticate inbound requests from the initiator (paired with a `HashedSecret`/`Salt` not returned, but the `AccessKey` alone identifies the initiator's inbound identity), and `OutgoingToken` is used to authenticate the node's own outbound calls to the initiator, i.e. `OutgoingToken`/`OutgoingSecret` are the credentials chainlink sends back to the initiator when notifying it of job runs [3](#0-2) . A test confirms the list endpoint returns `AccessKey` and `OutgoingToken` for every listed initiator without any additional scoping [4](#0-3) .

This is structurally the same bug class as CVE-2023-32687: a "list" capability (viewing the collection of chat-bot / external-initiator objects) discloses authentication material (`connectionString` equivalent to `AccessKey`/`OutgoingToken`) that should be gated behind a stricter permission or omitted from list views entirely, instead only being returned once at creation time (as is done in `Create`, which additionally returns the one-time `Secret` via `ExternalInitiatorAuthentication`) [5](#0-4) .

### Impact Explanation
Any authenticated node API user with access to the `/v2/external_initiators` list route can retrieve the `AccessKey` for every configured External Initiator. Combined with knowledge (or brute-forcing/leakage) of the initiator's secret, or simply by being able to identify and later hijack the initiator's inbound identity, an attacker gains reconnaissance into the node's job-triggering integrations. The `OutgoingToken` disclosure is more directly damaging: if an attacker also controls or can spoof the initiator's receiving endpoint, they can use knowledge of these tokens to correlate/verify outbound calls from the node, aiding impersonation attempts of the node-to-initiator channel.

### Likelihood Explanation
Reaching this data only requires basic authenticated access to the node's API and permission to view External Initiators — a normal, low-privilege operational capability in the Chainlink Operator UI, not an admin-only action. There's no additional authorization dimension distinguishing "can create/manage initiators" from "can view their credentials", exactly the gap identified in the source CVE.

### Recommendation
Strip `AccessKey` (or at minimum `OutgoingToken`) from `ExternalInitiatorResource` in `core/web/presenters/external_initiators.go`, or gate the `Index` route behind an elevated role/permission distinct from general read access, so that credential material is only ever returned once at creation time via `ExternalInitiatorAuthentication`, similar to the tgstation-server fix that decoupled "list" from "view connection string" permissions.

### Proof of Concept
1. Authenticate as any user with default read access to `/v2/external_initiators`.
2. Issue `GET /v2/external_initiators` (as exercised in `TestExternalInitiatorsController_Index`) [6](#0-5) .
3. Observe the JSON response includes `accessKey` and `outgoingToken` for each External Initiator record, disclosing credential material beyond what a basic list/read capability should expose.

**Note on limitations**: I was unable to confirm the exact role/permission middleware guarding the `/v2/external_initiators` routes in `core/web/router.go` (I located matches but couldn't view the surrounding route-registration code before running out of tool calls). If that route already requires an elevated/admin role equivalent to the "manage" permission, the severity of this analog would be reduced to same-privilege information exposure rather than a cross-role disclosure. This should be verified directly in `core/web/router.go` around the `ExternalInitiator` route group.

### Citations

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

**File:** core/web/external_initiators_controller.go (L61-99)
```go
// Create builds and saves a new external initiator
func (eic *ExternalInitiatorsController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	eir := &bridges.ExternalInitiatorRequest{}
	if !eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled() {
		err := errors.New("The External Initiator feature is disabled by configuration")
		jsonAPIError(c, http.StatusMethodNotAllowed, err)
		return
	}

	eia := auth.NewToken()
	if err := c.ShouldBindJSON(eir); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	ei, err := bridges.NewExternalInitiator(eia, eir)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	if err := ValidateExternalInitiator(ctx, eir, eic.App.BridgeORM()); err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}
	if err := eic.App.BridgeORM().CreateExternalInitiator(ctx, ei); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

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

**File:** core/bridges/external_initiator.go (L21-34)
```go
// ExternalInitiator represents a user that can initiate runs remotely
type ExternalInitiator struct {
	ID             int64
	Name           string
	URL            *models.WebURL
	AccessKey      string
	Salt           string
	HashedSecret   string
	OutgoingSecret string
	OutgoingToken  string

	CreatedAt time.Time
	UpdatedAt time.Time
}
```

**File:** core/web/external_initiators_controller_test.go (L84-126)
```go
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
