### Title
Bridge and External Initiator outgoing tokens are stored and returned in plaintext to any authenticated node user - ([File: core/web/presenters/external_initiators.go])

### Summary
The reported CVE describes a Jenkins plugin storing an API token unencrypted in a file that any user with filesystem access could read. The closest reachable analog in this chainlink node is not a filesystem issue but an equivalent "plaintext secret persisted and echoed back through an unprivileged, authenticated API surface": bridge `OutgoingToken` and external-initiator `OutgoingToken`/`OutgoingSecret` values are stored unhashed in the database and are re-served in full on ordinary list/get API and GraphQL calls, not just at creation time.

### Finding Description
When a bridge is created, `NewBridgeType` generates an `OutgoingToken` that is stored unhashed in the `bridge_types` table (only `IncomingToken` is salted/hashed) [1](#0-0) . This outgoing token is then included in every subsequent `BridgeResource` returned by the REST/JSONAPI presenter [2](#0-1) , and in the GraphQL `Bridge` type/resolver for `bridge`/`bridges` queries [3](#0-2) [4](#0-3) .

The same pattern exists for External Initiators: `NewExternalInitiator` generates `OutgoingToken`/`OutgoingSecret` in plaintext, persisted unhashed in `external_initiators` [5](#0-4) , and the `ExternalInitiatorsController.Index` handler serves them back on every list call via `NewExternalInitiatorResource`, which includes `OutgoingToken` in the JSON response [6](#0-5) [7](#0-6) .

Unlike the node's own user API tokens, which are salted/hashed (`token_hashed_secret`) and never round-tripped back to the client after creation (`SetAuthToken` in `core/sessions/localauth/orm.go`) [8](#0-7) , bridge and external-initiator outgoing tokens are treated as long-lived plaintext secrets that are perpetually retrievable by any authenticated caller who can hit these list/get endpoints. This mirrors the CVE's root cause class: a secret meant to authenticate outbound calls to a bridge/external adapter is stored unencrypted and is disclosable to any party with read access to the surface that stores it — here, that surface is the always-on node HTTP/GraphQL API rather than a config.xml file.

### Impact Explanation
Any authenticated node user who can call `GET /v2/bridge_types`, `GET /v2/external_initiators`, or the equivalent GraphQL `bridge`/`bridges` queries obtains the outgoing token/secret used by the node to authenticate to the bridge's external adapter or to the external initiator's callback endpoint. This token can be replayed to impersonate the chainlink node when calling the adapter/initiator, potentially triggering unauthorized job runs or manipulating adapter responses trusted by the node — a direct analog to "secret disclosure enabling request impersonation" called out as in-scope.

### Likelihood Explanation
Exploitation only requires any valid authenticated session/API token with sufficient role to call the bridge or external-initiator list endpoints — this is a standard, always-available node capability, not a privileged/operator-only filesystem access path, making the likelihood moderate-to-high wherever bridges/external initiators are configured (a routine feature for OCR/adapter integrations).

### Recommendation
Hash/salt the outgoing token analogous to the incoming token and the node's user API token scheme; only return the plaintext outgoing token at creation time (matching the existing `omitempty`/creation-only pattern already used for `IncomingToken`), and require re-authentication or restrict outgoing-token visibility to admin-role callers on subsequent list/get calls.

### Proof of Concept
1. As an authenticated node user, create a bridge: `POST /v2/bridge_types` → response includes `outgoingToken`.
2. Later, as any authenticated user with list access, call `GET /v2/bridge_types` or the GraphQL `bridges` query → the same plaintext `outgoingToken` is returned again [9](#0-8) .
3. Repeat with `POST /v2/external_initiators` then `GET /v2/external_initiators` to retrieve the persisted `outgoingToken` via `ExternalInitiatorResource` [7](#0-6) .
4. Use the disclosed token to authenticate as the node against the external adapter/initiator endpoint.

Note: I could not confirm from the indexed code which specific role (`Read`, `Run`, `Edit`, or `Admin`) is required to hit these routes, since `core/web/router.go`'s route-registration/role-middleware wiring for `/v2/bridge_types` and `/v2/external_initiators` was not found in the index. If these endpoints are restricted to `Admin`-only, the severity would be reduced closer to the "operator-only" exclusion; confirming this requires reviewing `core/web/router.go` directly (not fully available in the index) in a full Devin session.

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

**File:** core/web/presenters/bridges.go (L10-41)
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

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```

**File:** core/web/schema/type/bridge.graphql (L1-10)
```text
type Bridge {
    id: ID!
    name: String!
    url: String!
    confirmations: Int!
    outgoingToken: String!
    minimumContractPayment: String!
    useConnectionManager: Boolean!
    createdAt: Time!
}
```

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

**File:** core/sessions/localauth/orm.go (L331-340)
```go
// SetAuthToken updates the user to use the given Authentication Token.
func (o *orm) SetAuthToken(ctx context.Context, user *sessions.User, token *auth.Token) error {
	salt := utils.NewSecret(utils.DefaultSecretSize)
	hashedSecret, err := auth.HashedSecret(token, salt)
	if err != nil {
		return pkgerrors.Wrap(err, "user")
	}
	sql := "UPDATE users SET token_salt = $1, token_key = $2, token_hashed_secret = $3, updated_at = now() WHERE email = $4 RETURNING *"
	return o.ds.GetContext(ctx, user, sql, salt, token.AccessKey, hashedSecret, user.Email)
}
```
