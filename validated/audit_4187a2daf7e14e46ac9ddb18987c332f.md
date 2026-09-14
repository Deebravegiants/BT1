### Title
Bridge `OutgoingToken` Authentication Secret Stored in Plaintext and Disclosed via Read-Only Bridge API - ([File: core/bridges/bridge_type.go])

### Summary
The Jenkins JIRA Steps Plugin advisory (CVE-2023-24439) is a plaintext-secret-storage bug (CWE-256/312): a credential is persisted unencrypted where any actor with read access to the store can view it. Chainlink has a direct analog: the `BridgeType.OutgoingToken` used to authenticate the node's outgoing calls to an external adapter/bridge is stored in plaintext in the `bridge_type` table (unlike the `IncomingToken`, which is hashed+salted), and this plaintext value is returned by the standard bridge read endpoints (`Index`/`Show`) to any authenticated API caller who can query `/v2/bridge_types`, without any role gating beyond ordinary authenticated access.

### Finding Description
`BridgeType` stores `IncomingTokenHash` (hashed with salt) but keeps `OutgoingToken` as a raw plaintext field, both in the Go struct and in the `outgoing_token` DB column: [1](#0-0) 

`NewBridgeType` generates the outgoing token as an unencrypted random secret and stores it verbatim for persistence, contrasted with the incoming token which is hashed before storage: [2](#0-1) 

Unlike `IncomingToken`, which the presenter only emits on creation (`omitempty` json tag), `OutgoingToken` is unconditionally serialized in every `BridgeResource`, including for the `Index` (list) and `Show` (single-bridge lookup) endpoints — not just at creation time: [3](#0-2) 

The `Index` and `Show` controller handlers construct this resource straight from the ORM-loaded `BridgeType` and return it as-is for any authenticated read request: [4](#0-3) 

The same pattern repeats for `ExternalInitiator.OutgoingSecret`/`OutgoingToken`, which are also stored plaintext in the `external_initiators` table and returned by `ExternalInitiatorsController.Index`: [5](#0-4) [6](#0-5) [7](#0-6) 

### Impact Explanation
`OutgoingToken`/`OutgoingSecret` are the credentials the bridge/external-initiator uses to authenticate its own outgoing callback requests back into the Chainlink node (job run resumption endpoints). Because these are stored and returned unencrypted, any authenticated node API user who can call the read-only bridge/external-initiator listing endpoints obtains the plaintext secret. This secret can then be replayed by that user (or anyone they leak it to) to impersonate the bridge/external-initiator when calling back into the node, i.e., request impersonation of the external-initiator/bridge callback path — matching the "request impersonation" / "secret disclosure" criteria for a valid analog.

### Likelihood Explanation
Any user who is authenticated to the node's web API (via session or API token) and has permission to view bridges/external initiators — which for Chainlink's default roles is broadly available to non-admin roles as well — can trivially retrieve these secrets by calling `GET /v2/bridge_types` or `GET /v2/external_initiators`. No special privilege escalation or malicious-peer/network-layer conditions are required; it's a straightforward unprivileged-but-authenticated API read.

### Recommendation
- Hash and salt `OutgoingToken`/`OutgoingSecret` the same way `IncomingToken`/`HashedSecret` are handled, or otherwise avoid persisting/returning the raw value after initial creation.
- Change `BridgeResource.OutgoingToken` (and the `ExternalInitiatorResource`/`ExternalInitiatorAuthentication` equivalents) to `omitempty` and only populate it on the `Create` response, mirroring how `IncomingToken` is already handled, so subsequent `Index`/`Show` calls do not leak the plaintext secret.
- Consider rotating/encrypting these outgoing tokens at rest using the node's existing keystore encryption primitives.

### Proof of Concept
1. Create a bridge via `POST /v2/bridge_types` (obtains `OutgoingToken` once, as intended).
2. As any other authenticated API user with read access, call `GET /v2/bridge_types` or `GET /v2/bridge_types/{name}`.
3. Observe the response includes the same plaintext `outgoingToken` value (per `presenters.NewBridgeResource`), which was never hashed and is unconditionally serialized — confirming the secret is stored and disclosed in plaintext to any authenticated reader, not just the original creator.

### Citations

**File:** core/bridges/bridge_type.go (L57-68)
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
```

**File:** core/bridges/bridge_type.go (L70-102)
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
}
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

**File:** core/web/bridge_types_controller.go (L111-146)
```go
// Index lists Bridges, one page at a time.
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
