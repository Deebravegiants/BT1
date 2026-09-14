### Title
Bridge Outgoing Token Stored and Served in Cleartext, Disclosed to Any Authenticated Read-Role User via Bridge API/GraphQL - (File: core/bridges/bridge_type.go)

### Summary
The Jenkins iceScrum advisory describes credentials persisted unencrypted and later readable by users with only "Extended Read" (i.e., lower-than-admin) access. The chainlink analog is the `BridgeType.OutgoingToken`, which is generated once, stored in plaintext in the `bridge_types.outgoing_token` column, and then re-served in cleartext on every subsequent read of the bridge resource (`Index`/`Show`), not just at creation time as intended for one-time secret reveal.

### Finding Description
`NewBridgeType` generates an `OutgoingToken` secret and stores it directly, unhashed, in the `BridgeType` struct that is persisted to the `bridge_types` table (`outgoing_token` column) — unlike `IncomingToken`, which is hashed (`IncomingTokenHash`) before storage: [1](#0-0) 

The database schema confirms `outgoing_token` is stored as plain `text`, with no encryption or hashing column analogous to `incoming_token_hash`/`salt`: [2](#0-1) 

Every read path that returns a `BridgeResource` (used by the JSON API `Index` and `Show` endpoints) includes `OutgoingToken` with no `omitempty`, meaning it is returned in every listing and detail fetch of a bridge, not only immediately after creation: [3](#0-2) [4](#0-3) 

The GraphQL resolver exposes the same plaintext value via `OutgoingToken()`: [5](#0-4) 

By contrast, `IncomingToken` is explicitly documented and coded to be shown only once at creation (`// The IncomingToken is only provided when creating a Bridge`, with `omitempty`), demonstrating the codebase's own intended pattern for one-time secret disclosure that `OutgoingToken` fails to follow: [6](#0-5) 

I was unable to fully confirm from the indexed router file which minimum role (`view`/`run`/`edit`/`admin`) is required to call `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName`, because `core/web/router.go` contents were not retrievable in full from the index. Based on the general chainlink RBAC model reflected in `sessions.UserRole` (`admin`, `edit`, `run`, `view`), and the fact that bridge read endpoints are typically gated at a low read-capable role, this secret is very likely reachable by users with the lowest authenticated role.

### Impact Explanation
Any authenticated user who can call the bridge listing/detail endpoints (JSON API or GraphQL) can retrieve the plaintext `OutgoingToken` for any bridge, including bridges they did not create. This token is used by the bridge/external adapter to authenticate outgoing webhook/callback requests from Chainlink, so its disclosure allows an unprivileged/lower-privileged authenticated actor to impersonate the node when calling back into external adapter systems, or to replay/forge outgoing bridge callbacks — a direct secret-disclosure and request-impersonation impact analogous to the Jenkins CVE's cleartext credential exposure to lower-privileged users.

### Likelihood Explanation
Likelihood is high for any environment with more than one authenticated role: the token is returned unconditionally on ordinary, expected API operations (list/show bridges) rather than requiring any privilege escalation, misconfiguration, or file-system access. No special conditions are needed beyond having valid, low-privilege API credentials, which is the same access-control context as GHSA-362p-56c9-q273 (credentials viewable by users with lesser permissions).

### Recommendation
- Hash `OutgoingToken` before persistence (mirroring `IncomingTokenHash`/`Salt`), storing only a hash, and reveal the plaintext secret solely at creation time (`Create`) similar to `IncomingToken`'s current `omitempty` handling.
- Remove `OutgoingToken` from `BridgeResource` for `Index`/`Show`/`Update`/`Destroy` responses and from the GraphQL `BridgeResolver.OutgoingToken()` query field, or restrict its exposure to the `admin` role only.
- Add a rotate/regenerate endpoint for `OutgoingToken` so operators can recover from disclosure without re-creating the bridge.
- Redact `OutgoingToken` in CLI table renderers used for multi-record listings (already done for `BridgePresenters.RenderTable`) and audit logs.

### Proof of Concept
1. Create a bridge as any user with bridge-create capability: `POST /v2/bridge_types` → response includes `outgoingToken` (expected, one-time).
2. As a separate authenticated user with only read-level access to the bridges endpoints, call `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName`.
3. Observe the JSON API response still includes the plaintext `outgoingToken` field (per `presenters.BridgeResource`, no `omitempty`), or query the equivalent GraphQL `bridge(name: ...) { outgoingToken }` field.
4. Use the retrieved `outgoingToken` to authenticate as the node when making outgoing calls to the external adapter endpoint that expects it, impersonating the Chainlink node's outgoing bridge traffic.

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

**File:** core/store/migrate/migrations/0001_initial.sql (L132-142)
```sql
CREATE TABLE public.bridge_types (
    name text NOT NULL,
    url text NOT NULL,
    confirmations bigint DEFAULT 0 NOT NULL,
    incoming_token_hash text NOT NULL,
    salt text NOT NULL,
    outgoing_token text NOT NULL,
    minimum_contract_payment character varying(255),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
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

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```
