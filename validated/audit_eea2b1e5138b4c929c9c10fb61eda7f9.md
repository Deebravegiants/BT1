### Title
Persisted external initiator secrets (`OutgoingToken`) disclosed on index/list of External Initiators - (File: core/web/presenters/external_initiators.go)

### Summary
Chainlink's External Initiator (EI) feature persists an `OutgoingToken` (a secret used to authenticate the node's outbound webhook callbacks to the initiator) alongside the EI record. When any authenticated user retrieves the list of external initiators, this secret is included in the JSON response — mirroring the CVE-2020-14301 pattern where sensitive credential material was embedded in a routinely-retrievable configuration/inventory dump rather than being redacted.

### Finding Description
`ExternalInitiator.OutgoingToken` is generated as a random secret at creation time [1](#0-0) . This same field is persisted in the `external_initiators` table via `CreateExternalInitiator` [2](#0-1) .

The list/index endpoint `GET /v2/external_initiators` builds an `ExternalInitiatorResource` for every stored EI and includes `OutgoingToken` directly in the serialized response, with no redaction: [3](#0-2) . The controller wires this straight from the ORM query to the JSON:API response: [4](#0-3) .

This is confirmed by the test suite, which explicitly asserts that `OutgoingToken` for *other* EIs (`eiFoo`, `eiBar`) is returned in the paginated listing: [5](#0-4) .

Unlike the one-time `Secret`/`IncomingAccessKey`/`OutgoingSecret` values, which are only ever returned once at creation time via `ExternalInitiatorAuthentication` on `POST /v2/external_initiators` [6](#0-5) , the `OutgoingToken` is stored in plaintext in the DB and re-exposed on every subsequent list call through `ExternalInitiatorResource`, analogous to libvirt re-exposing HTTP cookie secrets on every `dumpxml`.

### Impact Explanation
Any user with API access sufficient to call `GET /v2/external_initiators` (a routine inventory-listing endpoint, not a one-time provisioning response) can read the `outgoingToken` secret for every external initiator configured on the node. This token authenticates the node's outbound webhook calls back to the initiator, so its disclosure allows an attacker to impersonate the Chainlink node to the initiator's callback endpoint, or to replay/spoof the token elsewhere it might be checked, resulting in unauthorized job-run triggering or trust-boundary confusion between the node and the external initiator relationship.

### Likelihood Explanation
No special privilege beyond the ability to invoke the standard, frequently-used `GET /v2/external_initiators` listing endpoint is required; there's no cookie/dumpxml-equivalent "special action" needed — it's returned on ordinary listing/pagination, so any client with access to this route (any authenticated node API user) is likely to encounter it, and the value is trivially recoverable rather than requiring guessing or brute force.

### Recommendation
Redact `OutgoingToken` (and any other stored secret material) from `ExternalInitiatorResource` used by the `Index`/list endpoints, mirroring the pattern already used for `Secret`/`OutgoingSecret`/`AccessKey`, which are only surfaced once at creation via `ExternalInitiatorAuthentication`. If the token must be recoverable by operators, expose it only through a explicit, audited "reveal" action rather than the default listing response, and consider storing the outgoing token hashed rather than in plaintext.

### Proof of Concept
1. Create an external initiator: `POST /v2/external_initiators {"name":"ei1"}` — response includes one-time `outgoingToken` (as in `TestExternalInitiatorsController_Create_success` [7](#0-6) ).
2. As any user permitted to call the listing endpoint, call `GET /v2/external_initiators`.
3. Observe the response includes `outgoingToken` for `ei1` (and every other configured EI) in plaintext, confirmed by the assertions in `TestExternalInitiatorsController_Index` [5](#0-4) .

### Citations

**File:** core/bridges/external_initiator.go (L36-57)
```go
// NewExternalInitiator generates an ExternalInitiator from an
// auth.Token, hashing the password for storage
func NewExternalInitiator(
	eia *auth.Token,
	eir *ExternalInitiatorRequest,
) (*ExternalInitiator, error) {
	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(eia, salt)
	if err != nil {
		return nil, pkgerrors.Wrap(err, "error hashing secret for external initiator")
	}

	return &ExternalInitiator{
		Name:           strings.ToLower(eir.Name),
		URL:            eir.URL,
		AccessKey:      eia.AccessKey,
		HashedSecret:   hashedSecret,
		Salt:           salt,
		OutgoingToken:  utils.NewSecret(utils.DefaultSecretSize),
		OutgoingSecret: utils.NewSecret(utils.DefaultSecretSize),
	}, nil
}
```

**File:** core/bridges/orm.go (L227-243)
```go
// CreateExternalInitiator inserts a new external initiator
func (o *orm) CreateExternalInitiator(ctx context.Context, externalInitiator *ExternalInitiator) (err error) {
	query := `INSERT INTO external_initiators (name, url, access_key, salt, hashed_secret, outgoing_secret, outgoing_token, created_at, updated_at)
	VALUES (:name, :url, :access_key, :salt, :hashed_secret, :outgoing_secret, :outgoing_token, now(), now())
	RETURNING *
	`
	err = o.transact(ctx, false, func(tx *orm) error {
		var stmt *sqlx.NamedStmt
		stmt, err = tx.ds.PrepareNamedContext(ctx, query)
		if err != nil {
			return pkgerrors.Wrap(err, "failed to prepare named stmt")
		}
		defer stmt.Close()
		return pkgerrors.Wrap(stmt.GetContext(ctx, externalInitiator, externalInitiator), "failed to load external_initiator")
	})
	return pkgerrors.Wrap(err, "CreateExternalInitiator failed")
}
```

**File:** core/web/presenters/external_initiators.go (L12-38)
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

// NewExternalInitiatorAuthentication creates an instance of ExternalInitiatorAuthentication.
func NewExternalInitiatorAuthentication(
	ei bridges.ExternalInitiator,
	eia auth.Token,
) *ExternalInitiatorAuthentication {
	var result = &ExternalInitiatorAuthentication{
		Name:           ei.Name,
		AccessKey:      ei.AccessKey,
		Secret:         eia.Secret,
		OutgoingToken:  ei.OutgoingToken,
		OutgoingSecret: ei.OutgoingSecret,
	}
	if ei.URL != nil {
		result.URL = *ei.URL
	}
	return result
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

**File:** core/web/external_initiators_controller_test.go (L129-154)
```go
func TestExternalInitiatorsController_Create_success(t *testing.T) {
	t.Parallel()

	app := cltest.NewApplicationWithConfig(t,
		configtest.NewGeneralConfig(t, func(c *chainlink.Config, s *chainlink.Secrets) {
			c.JobPipeline.ExternalInitiatorsEnabled = new(true)
		}))
	require.NoError(t, app.Start(t.Context()))

	client := app.NewHTTPClient(nil)

	resp, cleanup := client.Post("/v2/external_initiators",
		bytes.NewBufferString(`{"name":"bitcoin","url":"http://without.a.name"}`),
	)
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusCreated)
	ei := &presenters.ExternalInitiatorAuthentication{}
	cltest.ParseJSONAPIResponse(t, resp, ei)

	assert.Equal(t, "bitcoin", ei.Name)
	assert.Equal(t, "http://without.a.name", ei.URL.String())
	assert.NotEmpty(t, ei.AccessKey)
	assert.NotEmpty(t, ei.Secret)
	assert.NotEmpty(t, ei.OutgoingToken)
	assert.NotEmpty(t, ei.OutgoingSecret)
}
```
