### Title
Bridge outgoing token disclosed to any authenticated (view-role) user via bridge read APIs - (File: core/web/presenters/bridges.go)

### Summary
The trudesk CVE-2022-1893 is about sensitive information (auth material) not being stripped before it is returned/stored in an API response. The analogous pattern in this codebase is in the bridge presenter/resolver layer: the `OutgoingToken` for an External Adapter bridge is a non-`omitempty` field that is always serialized into every bridge read response (REST `Index`/`Show`, and GraphQL `bridges`/`bridge` queries), unlike `IncomingToken`, which is explicitly commented as "only provided when creating a Bridge" and marked `omitempty`.

### Finding Description
`BridgeResource` in `core/web/presenters/bridges.go` always includes `OutgoingToken` in the serialized JSON: [1](#0-0) 

`NewBridgeResource` populates it unconditionally from the stored `bridges.BridgeType.OutgoingToken`: [2](#0-1) 

This resource is returned as-is from `BridgeTypesController.Index` (list all bridges) and `BridgeTypesController.Show` (get one bridge by name): [3](#0-2) 

The same value is exposed via GraphQL through `BridgeResolver.OutgoingToken()` and the `bridges`/`bridge` queries/schema, which declare `outgoingToken: String!` as a normal, always-present field (not gated like the one-time `incomingToken` returned only from `CreateBridgeSuccess`): [4](#0-3) [5](#0-4) 

By contrast, `BridgeType.IncomingTokenHash`/`Salt` (the hashed incoming credential used to authenticate external-adapter callbacks) are never surfaced, and `IncomingToken` (the plaintext, one-time value) is explicitly `omitempty` and only attached right after creation in `BridgeTypesController.Create`: [6](#0-5) 

This shows the developers understood incoming credentials must not be re-exposed, but the outgoing token — which is a bearer secret sent by the node to the external adapter/bridge on every job run and is used by adapters to validate that a request genuinely originated from this Chainlink node — was not treated with the same care and is persistently returned on every subsequent read.

### Impact Explanation
Any authenticated node operator user (including lower-privileged roles that can only view/query bridges, not just admins who created them) can retrieve the bridge's `OutgoingToken` at any time after creation via `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, or the GraphQL `bridges`/`bridge` queries. If bridge read access is available to non-admin roles (e.g., "view"), this constitutes unauthorized disclosure of a secret that should be removed before storage/transfer to lower-privileged callers — mirroring the trudesk CVE's "Improper Removal of Sensitive Information Before Storage or Transfer" bug class. Disclosure of the outgoing token lets a party who obtains an API response (e.g., through a lower-privileged read-only account, logging, or a leaked response) impersonate the node when calling the external adapter/bridge, potentially manipulating data fed back into job pipelines.

### Likelihood Explanation
Likelihood is limited by the fact that reading bridges still requires being an authenticated node API user; this is not exploitable by a fully anonymous actor. However, because the token is returned on every ordinary listing/show call (not just at creation time, as is the case for `IncomingToken`), any user account with bridge-read privileges — which may be broader than the admin/edit role required to create or rotate bridges — will have standing access to this secret indefinitely, without needing to perform any privileged action.

### Recommendation
- Do not include `OutgoingToken` in `BridgeResource`/`BridgeResolver` for routine read (`Index`/`Show`/`bridges`/`bridge`) responses. Only surface it (or a masked/redacted form) at the point where it is set/rotated, mirroring the `IncomingToken` (`omitempty`, only attached in `Create`) pattern.
- If callers legitimately need to know whether an outgoing token is configured, expose a boolean flag (similar to `HasActiveAPIToken` in `UserResource`) instead of the raw token value.
- Restrict any endpoint that must return the raw `OutgoingToken` to admin-only, password-reauthenticated flows, consistent with how `NewAPIToken`/`DeleteAPIToken` require password re-verification before exposing token material.

### Proof of Concept
1. Create a bridge as an admin: `POST /v2/bridge_types` with a valid `BridgeTypeRequest`; the response includes both `incomingToken` and `outgoingToken` (expected, one-time).
2. As any authenticated user with bridge-read access (not necessarily admin), call `GET /v2/bridge_types/<bridgeName>` or `GET /v2/bridge_types` (or the GraphQL `bridges { results { outgoingToken } }` query).
3. Observe that `outgoingToken` (the bearer secret shared with the external adapter) is returned in full every time, with no redaction, unlike `incomingToken`, confirming persistent disclosure of stored sensitive information via ordinary read APIs.

Note: I was unable to fully confirm within available tool calls whether GraphQL bridge queries are restricted to admin-only role or allow the lower "view"/"run" roles (the grep for `authenticateUser`/role-check calls in `core/web/resolver/auth.go` was queued but its contents weren't retrieved before the iteration limit). If bridge reads are in fact restricted strictly to admin users only, the cross-role-privilege impact would be reduced, though the token would still be persistently exposed beyond its intended one-time-disclosure design.

### Citations

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

**File:** core/web/presenters/bridges.go (L29-41)
```go
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

**File:** core/web/bridge_types_controller.go (L98-108)
```go
	resource := presenters.NewBridgeResource(*bt)
	resource.IncomingToken = bta.IncomingToken

	btc.App.GetAuditLogger().Audit(audit.BridgeCreated, map[string]any{
		"bridgeName":                   bta.Name,
		"bridgeConfirmations":          bta.Confirmations,
		"bridgeMinimumContractPayment": bta.MinimumContractPayment,
		"bridgeURL":                    bta.URL,
	})

	jsonAPIResponse(c, resource, "bridge")
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

**File:** core/web/schema/type/bridge.graphql (L1-34)
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

# BridgePayload defines the response to fetch a single bridge by name
union BridgePayload = Bridge | NotFoundError

# BridgesPayload defines the response when fetching a page of bridges
type BridgesPayload implements PaginatedPayload {
    results: [Bridge!]!
    metadata: PaginationMetadata!
}

# CreateBridgeInput defines the input to create a bridge
input CreateBridgeInput {
    name: String!
    url: String!
    confirmations: Int!
    minimumContractPayment: String!
    useConnectionManager: Boolean
}

# CreateBridgeSuccess defines the success response when creating a bridge
type CreateBridgeSuccess {
    bridge: Bridge!
    incomingToken: String!
}
```
