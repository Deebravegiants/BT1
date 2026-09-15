This confirms all the core claims accurately reflect the current codebase. Let me verify the router wiring and GraphQL resolver/query access control to complete validation.Audit Report

## Title
Bridge Outgoing Token (webhook authentication secret) exposed to View-role users via `GET /v2/bridge_types/:BridgeName` and GraphQL `bridge` query - ([File: core/web/bridge_types_controller.go])

## Summary
The `OutgoingToken` field of a bridge — a secret used to authenticate the Chainlink node's outgoing calls to an external adapter — is returned unredacted in `BridgeResource` via `NewBridgeResource`, and the REST route `GET /v2/bridge_types/:BridgeName` is wired without any role-restriction wrapper (`bt.Show`, unlike `Create`/`Update`/`Destroy` which use `auth.RequiresEditRole`). This lets any authenticated user with only the `View` role read the secret, confirmed directly by the RBAC test table marking this route `viewOnlyAllowed: true`.

## Finding Description
`BridgeResource` includes `OutgoingToken string `json:"outgoingToken"`` without any redaction logic, and `NewBridgeResource` copies `b.OutgoingToken` straight from the stored `bridges.BridgeType` value: [1](#0-0) [2](#0-1) 

The router confirms `GET /v2/bridge_types/:BridgeName` is bound to `bt.Show` with no role wrapper, while the mutating routes (`Create`, `Update`, `Destroy`) are wrapped in `auth.RequiresEditRole`: [3](#0-2) 

This is corroborated by the RBAC route test table, which explicitly marks `GET /v2/bridge_types/MOCK` as `viewOnlyAllowed: true`, meaning a `View`-role session is expected to succeed on this route without a 401/403: [4](#0-3) 

`View` is the lowest authenticated role and is only blocked from `Run`/`Edit`/`Admin`-gated handlers (`RequiresRunRole`, `RequiresEditRole`), neither of which wraps `bt.Show`: [5](#0-4) 

The `OutgoingToken` is a genuinely sensitive credential, generated as a 24-byte secret at bridge creation and stored/used to authenticate outbound webhook calls: [6](#0-5) 

The same field is also exposed unconditionally via GraphQL: the schema declares `outgoingToken: String!` as always-present, and `BridgeResolver.OutgoingToken()` returns it directly; the `bridge` query only requires `authenticateUser`, which grants access to any authenticated session regardless of role.

The security model clearly intends `Edit`/`Admin` roles to gate access to bridge secrets (as shown by `RequiresEditRole` wrapping the write operations), but the read path (`Show`/GraphQL `bridge` query) was not brought under the same gate — this is the broken security assumption.

## Impact Explanation
This maps to CWE-200 / secret exfiltration, an in-scope Chainlink impact category (key/secret exfiltration). A low-privileged, authenticated `View`-role user (e.g., a read-only monitoring/dashboard account, a legitimate and documented role tier) can retrieve any configured bridge's `OutgoingToken` — the credential used to authenticate the node's outbound calls to external adapters — via a single unauthenticated-by-role GET request or GraphQL query. Depending on how the downstream adapter validates this token, this could allow impersonation of node-to-adapter traffic or unauthorized triggering/manipulation of adapter behavior, which the `View` role is explicitly designed to prevent (per the RBAC model separating `View` from `Edit`/`Run`/`Admin`).

## Likelihood Explanation
High likelihood in any deployment using multiple role tiers (supported natively via local admin-created users, LDAP, or OIDC role mapping — a documented, standard feature, not a misconfiguration). Exploitation requires only a valid `View`-role session and one HTTP GET or GraphQL query; no timing, race conditions, or additional bypass are needed. The RBAC test suite itself demonstrates and expects this exact behavior (`viewOnlyAllowed: true`), so it is not a hypothetical/edge-case path but the intended, current behavior of the route.

## Recommendation
- Redact or omit `OutgoingToken` from `BridgeResource` (and the GraphQL `Bridge` type/`BridgeResolver.OutgoingToken()`) for sessions below `Edit` role, mirroring the existing `IncomingToken` `omitempty`/creation-only exposure pattern.
- Alternatively, wrap `GET /v2/bridge_types/:BridgeName` in `auth.RequiresEditRole` (consistent with `Create`/`Update`/`Destroy`), and gate the GraphQL `bridge` query/resolver behind an edit-or-above check instead of the generic `authenticateUser`.
- Audit `Index` (`GET /v2/bridge_types`) and other presenters/resolvers (e.g., `ExternalInitiatorResource.OutgoingToken`) for the same unredacted-secret-on-view-role pattern.

## Proof of Concept
1. As an admin, create a `View`-role user via `POST /v2/users`.
2. As admin, create a bridge via `POST /v2/bridge_types`; note the server-generated `outgoingToken` in the response.
3. Authenticate as the `View`-role user (obtain session cookie).
4. Send `GET /v2/bridge_types/<BridgeName>` using the `View` session.
5. Observe HTTP 200 with the JSON:API response body containing `"outgoingToken": "<secret>"`, matching the secret from step 2 — disclosed to a user who cannot create/update/delete bridges.
6. Equivalently, run the GraphQL query `{ bridge(name: "<BridgeName>") { ... on Bridge { outgoingToken } } }` under the same `View` session and observe identical disclosure.
7. This can be directly verified/extended as a Go test analogous to the existing `core/web/auth/auth_test.go` RBAC table entry for `{"GET", "/v2/bridge_types/MOCK", true, true, true}`, asserting the response body leaks `OutgoingToken` under a `View`-role session.

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

**File:** core/web/presenters/bridges.go (L29-42)
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

**File:** core/web/auth/auth_test.go (L213-231)
```go
// The following are admin only routes
var routesRolesMap = [...]routeRules{
	{"GET", "/v2/users", false, false, false},
	{"POST", "/v2/users", false, false, false},
	{"PATCH", "/v2/users", false, false, false},
	{"DELETE", "/v2/users/MOCK", false, false, false},
	{"PATCH", "/v2/user/password", true, true, true},
	{"POST", "/v2/user/token", true, true, true},
	{"POST", "/v2/user/token/delete", true, true, true},
	{"GET", "/v2/enroll_webauthn", true, true, true},
	{"POST", "/v2/enroll_webauthn", true, true, true},
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/web/auth/auth.go (L198-234)
```go
// RequiresRunRole extracts the user object from the context, and asserts the user's role is at least
// 'run'
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

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
