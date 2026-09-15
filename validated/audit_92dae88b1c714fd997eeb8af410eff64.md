All the code claims are confirmed as accurate against the current repository state. The `Show`/`Index` bridge endpoints in `core/web/router.go` L269/L271 have no `RequiresEditRole`/`RequiresAdminRole` wrapper (unlike `Create`/`Update`/`Destroy`), the `BridgeResource.OutgoingToken` field lacks `omitempty` and is populated on every fetch, and the GraphQL `BridgeResolver.OutgoingToken()` unconditionally returns the raw stored value. The role hierarchy in `core/web/auth/auth.go` (`view < run < edit < admin`) confirms "view" is the lowest authenticated role, and no check gates the bridge read endpoints at all — any authenticated user regardless of role can hit them.

Audit Report

## Title
Bridge `outgoingToken` credential is stored in plaintext and disclosed to any authenticated viewer-role user - (File: core/web/presenters/bridges.go)

## Summary
The Chainlink node stores each bridge's `OutgoingToken` (the credential the node uses to authenticate to external adapters) unhashed in the database, and unconditionally serializes it back on every `GET /v2/bridge_types/:BridgeName`, `GET /v2/bridge_types`, and GraphQL `bridge`/`bridges` query response. Unlike the read endpoints for `Create`/`Update`/`Destroy`, the router applies no role-elevation middleware to the read paths, so any authenticated user — including the lowest-privilege "view" role — can retrieve every bridge's outgoing credential.

## Finding Description
`NewBridgeType` generates `OutgoingToken` as a plaintext secret and stores it directly in the `bridge_types.outgoing_token` column, in contrast to `IncomingToken`, which is salted and hashed into `IncomingTokenHash` before persistence (`core/bridges/bridge_type.go` L55-101). The `BridgeResource` JSONAPI struct marks `IncomingToken` with `json:"incomingToken,omitempty"` (only populated at creation time) but marks `OutgoingToken` as `json:"outgoingToken"` with no `omitempty`, and `NewBridgeResource` always copies `b.OutgoingToken` into the response (`core/web/presenters/bridges.go` L10-41). The `BridgeTypesController.Show` and `Index` handlers call `presenters.NewBridgeResource` on every fetched bridge without any redaction (`core/web/bridge_types_controller.go` L111-146).

Critically, the router wires `GET /v2/bridge_types/:BridgeName` and `GET /v2/bridge_types` with no role wrapper at all — only session/token authentication via the `authv2` group — while `POST`, `PATCH`, and `DELETE` on the same resource are wrapped in `auth.RequiresEditRole` (`core/web/router.go` L268-273). Verified in `core/web/auth/auth.go`, `RequiresEditRole`/`RequiresAdminRole` explicitly reject `UserRoleView`, confirming "view" is the lowest role in the hierarchy (`view < run < edit < admin`), and since the bridge read routes have no such wrapper, a "view" role session/token is sufficient to reach `Show`/`Index`. This is corroborated by the RBAC test table explicitly marking `GET /v2/bridge_types/MOCK` and `GET /v2/bridge_types` as `viewOnlyAllowed: true` (`core/web/auth/auth_test.go` L227-230, referenced by the report). The identical exposure exists in GraphQL: the schema declares `outgoingToken: String!` as a non-nullable always-present field (`core/web/schema/type/bridge.graphql` L1-10), and `BridgeResolver.OutgoingToken()` returns `r.bridge.OutgoingToken` unconditionally with no role check inside the resolver (`core/web/resolver/bridge.go` L52-55).

No existing control redacts or gates this field for lower-privileged roles — the only asymmetry in the codebase is the intentional `omitempty` treatment already applied to `IncomingToken`, which was not extended to `OutgoingToken`.

## Impact Explanation
`OutgoingToken` is the credential the node itself presents to external adapters when making outbound calls, functioning like an API key. Any account provisioned with the "view" role — intended strictly for read-only monitoring/dashboard use — can enumerate `GET /v2/bridge_types` or query the GraphQL `bridges` field and obtain every configured bridge's outgoing secret in plaintext, without ever needing edit or admin privileges. This is a concrete credential/secret exfiltration vulnerability (CWE-522 class) that breaks the intended privilege boundary between "view" and "edit"/"admin" roles, and could allow the holder of a low-trust viewer credential to impersonate the node to adapters or misuse the token if the adapter trusts it for authorization.

## Likelihood Explanation
High. No special preconditions are required beyond possession of a valid "view"-role session or API token — a credential type Chainlink operators are expected to issue routinely to lower-trust parties (dashboards, external monitoring, support staff) per the documented role hierarchy. The exploit is a single unauthenticated-relative-to-role, read-only HTTP or GraphQL request, fully repeatable, and requires no race conditions, timing, or destructive side effects.

## Recommendation
- Add `omitempty` and creation-only population semantics to `OutgoingToken` in `BridgeResource` (`core/web/presenters/bridges.go`), mirroring `IncomingToken`'s treatment, or gate the `Show`/`Index` bridge routes behind `auth.RequiresEditRole` for the token field specifically.
- Redact `outgoingToken` from GraphQL responses for non-edit/admin roles, or restructure the GraphQL `Bridge` type so `outgoingToken` is only exposed via the `CreateBridgeSuccess` payload, consistent with how `incomingToken` is already scoped in `CreateBridgeSuccessResolver.IncomingToken()`.
- Encrypt or hash `outgoing_token` at rest, decrypting only internally when the node calls the adapter, never re-serializing it to any API consumer post-creation.
- Add RBAC regression tests asserting that "view" role responses for bridge read endpoints omit `outgoingToken`.

## Proof of Concept
1. As admin, `POST /v2/bridge_types` to create a bridge; capture the returned `outgoingToken`.
2. Create a second user with role `view` (`clsessions.UserRoleView`).
3. Authenticate as the view-role user and send `GET /v2/bridge_types/<bridge_name>` (or GraphQL `query { bridge(id: "<bridge_name>") { ... on Bridge { outgoingToken } } }`).
4. Observe the response returns HTTP 200 with the identical plaintext `outgoingToken` value from step 1, despite the request only carrying "view" role credentials — demonstrated by the absence of any role check on this route in `core/web/router.go` L271 and the unconditional field serialization in `core/web/presenters/bridges.go` L18/L37 and `core/web/resolver/bridge.go` L52-55. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/auth/auth.go (L217-234)
```go
// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```
