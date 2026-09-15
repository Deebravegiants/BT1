Based on the code I found, the `ExternalInitiatorResource` presenter used for the `GET /v2/external_initiators` listing endpoint returns the initiator's `AccessKey` and `OutgoingToken` in plaintext to any caller who can hit that route, mirroring the XWiki bug class of a REST listing endpoint leaking authentication-relevant secrets that should be redacted/never re-served after creation.

### Title
Plaintext `AccessKey` and `OutgoingToken` credentials disclosed via `GET /v2/external_initiators` listing response - (File: core/web/presenters/external_initiators.go)

### Summary
The `ExternalInitiatorsController.Index` handler serializes every stored external initiator using `presenters.ExternalInitiatorResource`, which includes the raw `AccessKey` and `OutgoingToken` fields in the JSON:API response body, returned on every call to the list endpoint — not just at creation time.

### Finding Description
`ExternalInitiatorResource` is defined with `AccessKey` and `OutgoingToken` as plain, unredacted `string` fields [1](#0-0) , and `NewExternalInitiatorResource` copies these directly from the stored `bridges.ExternalInitiator` record without hashing or masking [2](#0-1) . The `Index` handler of `ExternalInitiatorsController` builds a full page of these resources from the ORM and returns them via `paginatedResponse` for every GET request to `/v2/external_initiators` [3](#0-2) . This is confirmed by the existing test, which asserts the plaintext `AccessKey` and `OutgoingToken` are present in the listing response body on every page fetch [4](#0-3) .

This is architecturally analogous to the XWiki bug: a REST "list"/"get" endpoint re-serializes stored authentication material (there, obfuscated passwords; here, `AccessKey`/`OutgoingToken`) on every subsequent call rather than only exposing it once at creation, defeating any expectation that these values act as write-once bearer credentials. `OutgoingToken` in particular is a credential Chainlink itself uses to authenticate outbound webhook calls to the initiator's registered URL (`X-Chainlink-EA-AccessKey`/secret-style headers used elsewhere in the codebase), so its repeated disclosure to any caller with access to this route undermines the initiator's authentication boundary.

By contrast, the codebase already treats other similar values correctly: `BridgeResource.IncomingToken` is `omitempty` and only ever populated at creation time [5](#0-4) , and the CLI bridge presenter explicitly excludes the outgoing token from the multi-item table render [6](#0-5) . The external-initiator listing presenter breaks this pattern by always emitting `AccessKey` and `OutgoingToken`.

### Impact Explanation
Any actor with access to the `/v2/external_initiators` list route (an authenticated node API user, not necessarily an admin — the exact minimum role requirement for this route could not be fully confirmed from available router code) can repeatedly retrieve every external initiator's `AccessKey` and `OutgoingToken`. `AccessKey` is one half of the initiator's authentication credential pair (paired with a secret used to authenticate `POST` calls into Chainlink, per `AuthenticateExternalInitiator`) [7](#0-6) , and `OutgoingToken` is used by Chainlink to authenticate to the initiator's own URL. Disclosure of these values to a lower-privileged or unintended caller enables request impersonation of the external initiator relationship, which is a concrete authentication-material disclosure analogous to the CVE's password/secret leakage via REST listing.

### Likelihood Explanation
The route is a standard, always-registered REST GET endpoint (no special feature flag gates the `Index`/list action, unlike `Create` which checks `ExternalInitiatorsEnabled()`) [3](#0-2) . Any client capable of issuing an authenticated request to this path receives the secrets on every call, making exploitation trivial and repeatable, limited only by whatever role is required to reach `/v2/external_initiators` (not fully verified from available router code).

### Recommendation
Redact `AccessKey` and `OutgoingToken` from `ExternalInitiatorResource` (or mark them `omitempty`/mask them, following the `BridgeResource.IncomingToken` pattern) so they are only ever returned once, in the `ExternalInitiatorAuthentication` response at creation time, and never re-served via the listing/show endpoints.

### Proof of Concept
1. As an authenticated node user with access to `/v2/external_initiators`, create an external initiator via `POST /v2/external_initiators` to obtain its `AccessKey`/`OutgoingToken` once.
2. Call `GET /v2/external_initiators` (or the paginated variant) as the same or another authorized user.
3. Observe the response body contains the same plaintext `accessKey` and `outgoingToken` fields for every stored initiator, as demonstrated by the existing test assertions [8](#0-7) .

### Citations

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

**File:** core/web/presenters/external_initiators.go (L67-77)
```go
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

**File:** core/web/presenters/bridges.go (L16-18)
```go
	// The IncomingToken is only provided when creating a Bridge
	IncomingToken          string       `json:"incomingToken,omitempty"`
	OutgoingToken          string       `json:"outgoingToken"`
```

**File:** core/cmd/bridge_commands_test.go (L53-62)
```go
	// Render many resources
	buffer.Reset()
	ps := cmd.BridgePresenters{p}
	require.NoError(t, ps.RenderTable(r))

	output = buffer.String()
	assert.Contains(t, output, name)
	assert.Contains(t, output, url)
	assert.Contains(t, output, "10")
	assert.NotContains(t, output, outgoingToken)
```

**File:** core/bridges/external_initiator.go (L59-67)
```go
// AuthenticateExternalInitiator compares an auth against an initiator and
// returns true if the password hashes match
func AuthenticateExternalInitiator(eia *auth.Token, ea *ExternalInitiator) (bool, error) {
	hashedSecret, err := auth.HashedSecret(eia, ea.Salt)
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(hashedSecret), []byte(ea.HashedSecret)) == 1, nil
}
```
