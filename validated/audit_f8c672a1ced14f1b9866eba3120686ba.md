## Analysis

The Rancher advisory (GHSA-g7j7-h4q8-8w2f) describes plaintext storage of sensitive credentials directly on Kubernetes objects, retrievable by any authenticated user with read access to those objects via the API (no privilege escalation needed beyond a valid low-privilege session). The closest analog in chainlink is how `bridge_types` and `external_initiators` GET endpoints return plaintext outgoing secrets/tokens to any authenticated user, regardless of role.

### Title
Plaintext outgoing webhook credentials for Bridges and External Initiators are stored unencrypted and exposed via GET endpoints to any authenticated (view-role) user - (File: core/web/presenters/bridges.go, core/web/presenters/external_initiators.go)

### Summary
`BridgeType.OutgoingToken` and `ExternalInitiator.OutgoingToken`/`OutgoingSecret` are generated as plaintext random secrets and stored unhashed in the database, then rendered back in full on the `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` endpoints, which require only a valid authenticated session (no elevated role check).

### Finding Description
`bridges.NewBridgeType` generates `outgoingToken` as a random secret and stores it as plaintext in the `bridge_type` table (`OutgoingToken string \`db:"outgoing_token"\``), unlike `IncomingToken`, which is hashed (`IncomingTokenHash`, `Salt`) before storage. [1](#0-0) 

The `BridgeResource` presenter always serializes `OutgoingToken` (no `omitempty`), unlike `IncomingToken` which is `omitempty` and only populated on `Create`. [2](#0-1) 

Similarly, `ExternalInitiator.OutgoingSecret`/`OutgoingToken` are generated via `utils.NewSecret` and stored as plaintext columns (`outgoing_secret`, `outgoing_token`) with no hashing. [3](#0-2) [4](#0-3) 

The `ExternalInitiatorResource` presenter used by `Index` includes `OutgoingToken` in every listing response, confirmed directly by the test asserting `externalInitiators[0].OutgoingToken` equals the stored plaintext value. [5](#0-4) [6](#0-5) 

Route wiring shows these `Index`/`Show` endpoints require only generic session/token authentication, with no `RequiresEditRole`/`RequiresAdminRole` gate — unlike `Create`/`Update`/`Destroy`, which do require `RequiresEditRole`: [7](#0-6) 

### Impact Explanation
Any authenticated node-UI user with only "view" role (the lowest privilege tier, distinct from "edit"/"admin") can read the plaintext `OutgoingToken` for every configured bridge and the `OutgoingToken` for every external initiator via `GET /v2/bridge_types` and `GET /v2/external_initiators`. These outgoing tokens are used by chainlink to authenticate itself to external adapters/initiators (bridges) — leaking them lets a low-privileged user impersonate the node when calling out to those third-party services, or replay/forge outgoing-authenticated requests, similar in class to the Rancher issue where any reader of the object could retrieve plaintext credentials used by the platform to authenticate to external systems. This is a genuine cross-role confidentiality exposure: a "view" role account was never meant to obtain any operational secret.

### Likelihood Explanation
High for any deployment that grants "view" role accounts (a common, deliberately low-privilege tier in chainlink's RBAC) to inspect node configuration via the UI/API. No additional exploitation step is needed beyond calling the already-exposed, unauthenticated-in-role-terms `GET` endpoints with a valid session/API token of any role.

### Recommendation
- Do not return `OutgoingToken`/`OutgoingSecret` in `Index`/`Show` responses for bridges and external initiators; mark them `omitempty` and only populate on `Create` responses, mirroring the existing `IncomingToken` handling in `BridgeResource`.
- Alternatively, restrict `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` with `auth.RequiresEditRole` (or higher) so low-privilege "view" accounts cannot retrieve secrets needed only for administering integrations.
- Consider storing `OutgoingToken`/`OutgoingSecret` encrypted at rest (similar to Rancher's fix of moving secrets into a dedicated `Secret` object retrieved on demand) rather than as plaintext DB columns.

### Proof of Concept
1. As an admin, create a bridge: `POST /v2/bridge_types` with `{"name":"test","url":"http://adapter"}` — response returns `outgoingToken`.
2. Create/obtain a session for a user with role `view` only.
3. As the `view` user, call `GET /v2/bridge_types` or `GET /v2/bridge_types/test` — the response body includes the same plaintext `outgoingToken` field, confirmed by `core/web/bridge_types_controller_test.go` structure and the unconditional `OutgoingToken` field in `presenters.BridgeResource`.
4. Similarly, as the `view` user, call `GET /v2/external_initiators` — the plaintext `outgoingToken` for every initiator is returned, as demonstrated by the existing test assertion `assert.Equal(t, eiFoo.OutgoingToken, externalInitiators[0].OutgoingToken)` in `core/web/external_initiators_controller_test.go:126`.

### Citations

**File:** core/bridges/bridge_type.go (L57-101)
```go
type BridgeType struct {
	Name                   BridgeName    `db:"name"`
	URL                    models.WebURL `db:"url"`
	Confirmations          uint32        `db:"confirmations"`
	IncomingTokenHash      string        `db:"incoming_token_hash"`
	Salt                   string        `db:"salt"`
	OutgoingToken          string        `db:"outgoing_token"`
	MinimumContractPayment *assets.Link  `db:"minimum_contract_payment"`
	CreatedAt              time.Time     `db:"created_at"`
	UpdatedAt              time.Time     `db:"updated_at"`
	UseConnectionManager   bool          `db:"use_connection_manager" json:"useConnectionManager"`
}

// NewBridgeType returns a bridge type authentication (with plaintext
// password) and a bridge type (with hashed password, for persisting)
func NewBridgeType(btr *BridgeTypeRequest) (*BridgeTypeAuthentication,
	*BridgeType, error,
) {
	incomingToken := utils.NewSecret(24)
	outgoingToken := utils.NewSecret(24)
	salt := utils.NewSecret(24)

	hash, err := incomingTokenHash(incomingToken, salt)
	if err != nil {
		return nil, nil, err
	}

	return &BridgeTypeAuthentication{
		Name:                   btr.Name,
		URL:                    btr.URL,
		Confirmations:          btr.Confirmations,
		IncomingToken:          incomingToken,
		OutgoingToken:          outgoingToken,
		MinimumContractPayment: btr.MinimumContractPayment,
		UseConnectionManager:   btr.UseConnectionManager,
	}, &BridgeType{
		Name:                   btr.Name,
		URL:                    btr.URL,
		Confirmations:          btr.Confirmations,
		IncomingTokenHash:      hash,
		Salt:                   salt,
		OutgoingToken:          outgoingToken,
		MinimumContractPayment: btr.MinimumContractPayment,
		UseConnectionManager:   btr.UseConnectionManager,
	}, nil
```

**File:** core/web/presenters/bridges.go (L11-41)
```go
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

// GetName implements the api2go EntityNamer interface
func (r BridgeResource) GetName() string {
	return "bridges"
}

// NewBridgeResource constructs a new BridgeResource
func NewBridgeResource(b bridges.BridgeType) *BridgeResource {
	return &BridgeResource{
		// Uses the name as the id...Should change this to the id
		JAID:                   NewJAID(b.Name.String()),
		Name:                   b.Name.String(),
		URL:                    b.URL.String(),
		Confirmations:          b.Confirmations,
		OutgoingToken:          b.OutgoingToken,
		MinimumContractPayment: b.MinimumContractPayment,
		UseConnectionManager:   b.UseConnectionManager,
		CreatedAt:              b.CreatedAt,
	}
```

**File:** core/bridges/external_initiator.go (L21-57)
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

**File:** core/store/migrate/migrations/0001_initial.sql (L483-495)
```sql
CREATE TABLE public.external_initiators (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone,
    name text NOT NULL,
    url text,
    access_key text NOT NULL,
    salt text NOT NULL,
    hashed_secret text NOT NULL,
    outgoing_secret text NOT NULL,
    outgoing_token text NOT NULL
);
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

**File:** core/web/router.go (L263-273)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))

		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```
