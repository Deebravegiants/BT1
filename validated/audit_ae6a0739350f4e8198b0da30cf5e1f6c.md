## Analog Analysis: Long-lived External Initiator credentials permanently exposed via read-only list/index endpoint

### Title
Plaintext `AccessKey` and `OutgoingToken` for External Initiators permanently exposed to any authenticated viewer via `GET /v2/external_initiators` - (File: core/web/presenters/external_initiators.go)

### Summary
The Airflow advisory (GHSA-4g48-54q2-fg7q) describes secret-bearing connection fields (`access_key`, `connection_string`) that were not marked sensitive, so users with mere read access to the Connection UI/logs could see them. The chainlink analog is structurally similar but does not depend on a masker's field-name heuristics: the `ExternalInitiatorResource` presenter, used by the `GET /v2/external_initiators` index endpoint, unconditionally serializes the long-lived `AccessKey` and `OutgoingToken` credentials in plaintext, so any authenticated user who can call that endpoint gets standing access to these secrets, not just at creation time.

### Finding Description
`ExternalInitiator` credentials (`AccessKey`, `HashedSecret`, `OutgoingSecret`, `OutgoingToken`) authenticate inbound/outbound webhook traffic between the node and an external initiator service [1](#0-0) . By design, the plaintext one-time `Secret` is only meant to be returned once, at creation, via `ExternalInitiatorAuthentication` [2](#0-1) .

However, the list/read presenter `ExternalInitiatorResource`, returned by the `Index` handler on every subsequent `GET /v2/external_initiators` call, always includes `AccessKey` and `OutgoingToken` in plaintext with no redaction and no `omitempty`: [3](#0-2) 

The controller builds this resource straight from the ORM-loaded records for every initiator on every page of the index, with no field filtering: [4](#0-3) 

This is confirmed by the test asserting that `AccessKey` and `OutgoingToken` are returned on `GET /v2/external_initiators?...`: [5](#0-4) 

By contrast, the analogous `BridgeResource` presenter deliberately keeps `IncomingToken` (the one-time secret) `omitempty` and unset on normal reads, only populating it in the creation-flow response type — showing that the codebase is aware of the "don't leak the one-time secret on every read" pattern, but the `ExternalInitiator` presenter fails to apply the same restraint to its own long-lived credentials (`AccessKey`, `OutgoingToken`) used to authenticate every future request between chainlink and the initiator. [6](#0-5) 

This route sits behind the standard node HTTP session/API-token auth used for all `/v2/...` endpoints; I was unable to fully confirm from the index whether it additionally enforces a specific role tier (e.g. "view" vs "admin") beyond generic authentication, since the router role annotations for this route were not retrievable within the available tool budget — this is a gap in verification, not a claim that no role check exists.

### Impact Explanation
`AccessKey` and `OutgoingToken` are not one-time bootstrap secrets — they are the standing bearer-style credentials used on every external-initiator interaction: `AccessKey`/`Secret` authenticate inbound job-run trigger requests to the node (`X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret` headers, see `TestTokenAuthRequired_TokenCredentials`), and `OutgoingToken`/`OutgoingSecret` authenticate outbound callbacks from the node to the external initiator. Any authenticated user who can call `GET /v2/external_initiators` (which appears to be a low-privilege, read-only, listing endpoint, unlike `POST`/`DELETE`) can harvest `AccessKey` and `OutgoingToken` for every configured initiator, in perpetuity, without needing initial creation-time access. This enables request impersonation of the external initiator or forging authenticated job-run triggers if `AccessKey`/associated `Secret` can be derived or reused, matching the "concrete authentication bypass / key disclosure" bar. Impact severity is comparable to the Airflow CVE (Medium, confidentiality-only, no direct integrity/availability impact by itself), since the raw `Secret` (`HashedSecret`) itself is not exposed, but `AccessKey` and the full `OutgoingToken` are.

### Likelihood Explanation
Likelihood is high for any deployment using External Initiators (`ExternalInitiatorsEnabled`), since the exposure occurs on every ordinary paginated `GET /v2/external_initiators` call with no special conditions, misconfiguration, or logging accident required — unlike the Airflow bug, which required the value to be viewed in the Connection UI or accidentally logged. Here it's the documented, always-on behavior of the presenter used by the index route.

### Recommendation
Mirror the pattern already used for `BridgeResource`/`IncomingToken`: strip or omit `AccessKey` and `OutgoingToken` from `ExternalInitiatorResource` (the read/list presenter), and only return them once, from the dedicated creation-response type (`ExternalInitiatorAuthentication`), which is already scoped to `POST` create. If some other part of the UI legitimately needs to re-display `OutgoingToken` (e.g., for URL construction), consider truncating/masking it or gating it behind an elevated role, consistent with the intent of the Airflow fix (mark sensitive fields so they are hidden from users with only view access).

### Proof of Concept
1. Enable External Initiators (`JobPipeline.ExternalInitiatorsEnabled = true`).
2. `POST /v2/external_initiators` with any authenticated session/API key to create an initiator (or as any user with create rights).
3. As a separate, lower-privileged user who only has read/view access, call `GET /v2/external_initiators?size=50`.
4. Observe the response body includes, for every initiator, `accessKey` and `outgoingToken` in cleartext — reproducing exactly what `TestExternalInitiatorsController_Index` asserts: [7](#0-6)

### Citations

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

**File:** core/web/presenters/external_initiators.go (L12-20)
```go
// ExternalInitiatorAuthentication includes initiator and authentication details.
type ExternalInitiatorAuthentication struct {
	Name           string        `json:"name,omitempty"`
	URL            models.WebURL `json:"url"`
	AccessKey      string        `json:"incomingAccessKey,omitempty"`
	Secret         string        `json:"incomingSecret,omitempty"`
	OutgoingToken  string        `json:"outgoingToken,omitempty"`
	OutgoingSecret string        `json:"outgoingSecret,omitempty"`
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

**File:** core/web/presenters/bridges.go (L10-22)
```go
// BridgeResource represents a Bridge JSONAPI resource.
type BridgeResource struct {
	JAID
	Name          string `json:"name"`
	URL           string `json:"url"`
	Confirmations uint32 `json:"confirmations"`
	// The IncomingToken is only provided when creating a Bridge
	IncomingToken          string       `json:"incomingToken,omitempty"`
	OutgoingToken          string       `json:"outgoingToken"`
	MinimumContractPayment *assets.Link `json:"minimumContractPayment"`
	UseConnectionManager   bool         `json:"useConnectionManager"`
	CreatedAt              time.Time    `json:"createdAt"`
}
```
