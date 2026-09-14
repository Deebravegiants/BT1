### Title
Bridge and External Initiator `OutgoingToken`/`OutgoingSecret` credentials are persisted in plaintext and returned unredacted to any authenticated Read-role user via `GET /v2/bridge_types` and `GET /v2/external_initiators` - (File: core/web/presenters/bridges.go, core/web/presenters/external_initiators.go)

### Summary
Analogous to the Jenkins Xooa Plugin flaw (unencrypted deployment token stored and viewable by any user with access), the chainlink node stores the `OutgoingToken` (bridges) and `OutgoingToken`/`OutgoingSecret` (external initiators) in plaintext in the database, and unlike the `IncomingToken`/`IncomingAccessKey` (which are hashed/one-time-shown), these outgoing credentials are returned in full on every subsequent `Index`/`Show` API call to any authenticated user, regardless of role.

### Finding Description
`NewBridgeType` generates `OutgoingToken` as plaintext (never hashed) alongside a hashed `IncomingToken`: [1](#0-0) . Similarly, `NewExternalInitiator` stores `OutgoingToken` and `OutgoingSecret` as plaintext fields distinct from the hashed `HashedSecret` used for inbound authentication: [2](#0-1) .

Unlike the `IncomingToken`, which is only exposed once at creation time (`bridgeResource.IncomingToken = bta.IncomingToken` set only in `Create`, and marked `omitempty` in the presenter), the `OutgoingToken` field is unconditionally included on every response: [3](#0-2)  and [4](#0-3) . The `Index` and `Show` handlers for bridges call `NewBridgeResource`, which always populates `OutgoingToken`, so any call to `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` returns this plaintext outbound credential: [5](#0-4) .

The same pattern exists for external initiators: `ExternalInitiatorResource` always includes `OutgoingToken` (not `omitempty`), and `Index` lists all initiators with this field populated: [6](#0-5) , [7](#0-6) .

These outgoing tokens/secrets are the credentials the node itself uses to authenticate outbound calls to bridge/initiator endpoints (analogous to the Xooa "Deployment Token"), so their exposure via a routine list/show API call mirrors the advisory's root cause: a sensitive secret is stored and served unencrypted to any user with basic (non-admin) API access.

### Impact Explanation
Any authenticated user with at least Read role who can call `GET /v2/bridge_types` or `GET /v2/external_initiators` obtains the plaintext `OutgoingToken`/`OutgoingSecret` used by the node to authenticate to external bridge adapters and initiators. An attacker with this credential could impersonate the Chainlink node when calling those external services, or use the leaked secret to forge/replay authenticated callbacks depending on how the receiving external initiator validates the outgoing token. This is a secret-disclosure issue reachable via a standard, low-privilege authenticated GET request — not merely informational, since it discloses a live credential rather than a hash.

### Likelihood Explanation
High: no special privilege beyond a valid session/API token with Read access is required, and the disclosure occurs on the default `Index`/`Show` list endpoints that are exercised in normal node operation (e.g., Operator UI bridge list page), not a rare admin-only path.

### Recommendation
Do not return `OutgoingToken`/`OutgoingSecret` on `Index`/`Show` responses; treat them like `IncomingToken` (omit by default, or require re-authentication/regeneration to view, consistent with the `omitempty` pattern already used for `IncomingToken`). If the value must be retrievable, restrict it to a one-time reveal at creation and mask it (e.g., `xxxxx`) on subsequent reads, mirroring the `Secret`/`SecretURL` redaction pattern already used elsewhere in config (`core/store/models/secrets.go`).

### Proof of Concept
1. As any user with a valid session/API token that has at least Read role, call `GET /v2/bridge_types` (bridge `Index`, `core/web/bridge_types_controller.go` lines 112-122).
2. Inspect the JSON response body — each bridge resource includes `outgoingToken` in plaintext (`core/web/presenters/bridges.go` line 18).
3. Repeat with `GET /v2/external_initiators` (`core/web/external_initiators_controller.go` lines 50-59) — response includes `outgoingToken` in plaintext (`core/web/presenters/external_initiators.go` line 62).
4. Use the retrieved `outgoingToken` to authenticate as the node against the corresponding external bridge/initiator endpoint.

### Citations

**File:** core/bridges/bridge_type.go (L70-101)
```go
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

**File:** core/web/presenters/bridges.go (L10-42)
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
}
```

**File:** core/web/bridge_types_controller.go (L98-99)
```go
	resource := presenters.NewBridgeResource(*bt)
	resource.IncomingToken = bta.IncomingToken
```

**File:** core/web/bridge_types_controller.go (L112-146)
```go
func (btc *BridgeTypesController) Index(c *gin.Context, size, page, offset int) {
	ctx := c.Request.Context()
	bridges, count, err := btc.App.BridgeORM().BridgeTypes(ctx, offset, size)

	resources := make([]presenters.BridgeResource, 0, len(bridges))
	for _, bridge := range bridges {
		resources = append(resources, *presenters.NewBridgeResource(bridge))
	}

	paginatedResponse(c, "Bridges", size, page, resources, count, err)
}

// Show returns the details of a specific Bridge.
func (btc *BridgeTypesController) Show(c *gin.Context) {
	ctx := c.Request.Context()
	name := c.Param("BridgeName")

	taskType, err := bridges.ParseBridgeName(name)
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	bt, err := btc.App.BridgeORM().FindBridge(ctx, taskType)
	if errors.Is(err, sql.ErrNoRows) {
		jsonAPIError(c, http.StatusNotFound, errors.New("bridge not found"))
		return
	}
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
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
