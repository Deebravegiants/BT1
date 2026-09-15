Confirmed: `Bridge` and (by symmetry) `Bridges` GraphQL queries only require `authenticateUser`, which per the comment in `core/web/resolver/auth.go` grants access to any authenticated session with only the minimal "view" role — no edit/admin requirement. [1](#0-0) [2](#0-1) 

This confirms the claim's uncertain point: bridge reads are not admin-restricted; a "view"-role user can call `bridge`/`bridges` GraphQL queries (and correspondingly the REST `Index`/`Show` endpoints, which have no stricter role gating than standard authenticated session middleware) and receive `outgoingToken` in full on every read, unlike `incomingToken` which is `omitempty` and only set once at creation. [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

This is a real, concrete design asymmetry: the outgoing bridge token (a bearer secret used by the node to authenticate to the external adapter) is persistently readable by any authenticated user with only view-level privileges, whereas the incoming token is deliberately treated as a one-time secret. This maps to unauthorized secret disclosure to a lower-privileged (but still authenticated) role — an in-scope impact class (key/secret exfiltration via node API), since "view" role is a distinct, lower-privileged role from admin/edit, and the finding shows a concrete escalation from the minimal-privilege starting point (view-only session) to secret material disclosure that the codebase's own design intended to protect (as evidenced by the incoming-token handling).

Audit Report

## Title
Bridge `OutgoingToken` secret disclosed to any authenticated view-role user via REST and GraphQL bridge read APIs - (File: core/web/presenters/bridges.go)

## Summary
`BridgeResource.OutgoingToken` (`core/web/presenters/bridges.go` L10-22) is a non-`omitempty` field always populated from `bridges.BridgeType.OutgoingToken` in `NewBridgeResource` (L29-41), and is returned unconditionally by `BridgeTypesController.Index`/`Show` (`core/web/bridge_types_controller.go` L111-146) and by the GraphQL `bridge`/`bridges` queries via `BridgeResolver.OutgoingToken()` (`core/web/resolver/bridge.go` L52-55) and the `outgoingToken: String!` schema field. Unlike `IncomingToken`, which is `omitempty` and only populated once at creation time (`bridge_types_controller.go` L98-108), the outgoing token — a bearer secret used by the node to authenticate itself to the external adapter — is persistently exposed on every ordinary read call.

## Finding Description
The GraphQL `Bridge` query only calls `authenticateUser(ctx)` (`core/web/resolver/query.go` L27-38), which per its own doc comment in `core/web/resolver/auth.go` (L11-17) grants access based purely on having an authenticated session — "presence of user inherently provides 'view' access" — with no elevated role check (contrast with `authenticateUserCanEdit`/`authenticateUserIsAdmin` used elsewhere for privileged mutations, `auth.go` L19-55). The REST `Index`/`Show` handlers apply the same standard session-authenticated middleware without additional role gating for bridge reads. Because `BridgeResource` serializes `OutgoingToken` unconditionally (no `omitempty`, no redaction), any session — even one restricted to the lowest "view" role — that can query bridges will receive the raw outgoing token in the response body, indefinitely, for the lifetime of the bridge. This directly parallels the trudesk CVE pattern: sensitive credential material that should be removed/redacted before being returned to lower-privileged callers is instead persistently serialized into every read response.

## Impact Explanation
The outgoing token is a secret shared between the Chainlink node and the external adapter, used by the adapter to verify requests genuinely originate from the node. Disclosure to a "view"-role account (a real, distinct, lower-privileged role than admin/edit in this codebase's role model) allows a low-privileged authenticated actor to obtain this secret and impersonate the node to the external adapter, potentially manipulating adapter behavior/data fed back into job runs — an in-scope "key/secret exfiltration via node API" impact.

## Likelihood Explanation
Exploitation only requires a "view"-role authenticated session (the minimum authorization level in the system), which is a concrete escalation from the lowest available authenticated privilege to persistent secret disclosure — not requiring admin/edit access, host access, or any misconfiguration. Every ordinary listing or show call reproduces the disclosure, making it fully repeatable and low-effort for anyone with such an account.

## Recommendation
- Remove `OutgoingToken` from `BridgeResource`/`BridgeResolver` responses for routine `Index`/`Show`/`bridges`/`bridge` reads; mark it `omitempty` and only populate it at creation/rotation, mirroring the `IncomingToken` pattern.
- If callers need to know a token is configured, expose a boolean flag instead of the raw value.
- Gate any endpoint that must return the raw `OutgoingToken` behind `authenticateUserIsAdmin` (or stricter), consistent with other secret-exposing flows in the codebase.

## Proof of Concept
1. Create a session with `sessions.UserRoleView` (lowest privilege) authenticated via the standard session cookie flow.
2. As that session, call GraphQL `query { bridges { results { name outgoingToken } } }` or REST `GET /v2/bridge_types` / `GET /v2/bridge_types/:BridgeName`.
3. Observe `outgoingToken` is returned in full for every bridge, confirming that `authenticateUser` (view-level) is sufficient to read the secret via `core/web/resolver/query.go` L27-38 and `core/web/presenters/bridges.go` L10-22/29-41, with no redaction or role escalation required.

### Citations

**File:** core/web/resolver/auth.go (L11-17)
```go
// Authenticates the user from the session cookie, presence of user inherently provides 'view' access.
func authenticateUser(ctx context.Context) error {
	if _, ok := auth.GetGQLAuthenticatedSession(ctx); !ok {
		return unauthorizedError{}
	}
	return nil
}
```

**File:** core/web/resolver/query.go (L27-38)
```go
// Bridge retrieves a bridges by name.
func (r *Resolver) Bridge(ctx context.Context, args struct{ ID graphql.ID }) (*BridgePayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	name, err := bridges.ParseBridgeName(string(args.ID))
	if err != nil {
		return nil, err
	}

	bridge, err := r.App.BridgeORM().FindBridge(ctx, name)
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
