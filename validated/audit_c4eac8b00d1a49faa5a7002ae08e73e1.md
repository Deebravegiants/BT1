All findings in the claim are confirmed by the actual code. The `GET /v2/bridge_types/:BridgeName` route is registered without any role wrapper, unlike its sibling `Create`/`Update`/`Destroy` actions, and the `Show` handler serializes the full bridge record including the unconditional `OutgoingToken` field.

Audit Report

## Title
Bridge secret `OutgoingToken` disclosed to low-privileged (view-only) authenticated users - (File: `core/web/router.go`)

## Summary
The `GET /v2/bridge_types/:BridgeName` route is registered with no role wrapper, while its sibling write actions (`Create`, `Update`, `Destroy`) on the same resource are wrapped with `auth.RequiresEditRole`. As a result, any authenticated user regardless of role — including `UserRoleView` — can retrieve a bridge's plaintext `OutgoingToken` secret via this endpoint or the equivalent GraphQL `bridge` query.

## Finding Description
In `core/web/router.go`, the bridge-types routes show the asymmetry directly: [1](#0-0) 
`Create`, `Update`, and `Destroy` are wrapped with `auth.RequiresEditRole`, but `Show` (bound to `GET /v2/bridge_types/:BridgeName`) has no role wrapper and only passes through generic session/API-token authentication. This is directly corroborated by the RBAC test matrix, which marks this exact route as `viewOnlyAllowed: true`: [2](#0-1) 
The `Show` handler performs no extra per-field authorization and serializes the full bridge record via `presenters.NewBridgeResource`, and that presenter unconditionally includes `OutgoingToken` in the JSON output — unlike `IncomingToken`, which is `omitempty` and only ever populated at creation time: [3](#0-2) 
The stored `BridgeType.OutgoingToken` is a 24-byte random secret kept and returned in plaintext (as opposed to `IncomingTokenHash`, which is hashed), so nothing in the storage or serialization layer redacts it for lower-privileged callers.

## Impact Explanation
`OutgoingToken` is the credential the node uses to prove to an external bridge/adapter that a request originated from the Chainlink node. Disclosure of this secret to a `View`-role account — a role intended for read-only, non-sensitive access — lets that account obtain a bridge-authentication credential it should not have, enabling potential impersonation of the node to the external adapter depending on how the adapter validates the token. This falls within the "key/secret exfiltration" and "cross-role privilege confusion" impact categories.

## Likelihood Explanation
Exploitation requires only an existing `View`-role session or API token (the lowest privilege tier explicitly supported by the RBAC system) and a single unauthenticated-in-the-privilege-sense `GET` request to a known/enumerable bridge name. No admin, host, or database access is needed, and the behavior is deterministic and repeatable on any deployment that issues view-only accounts (common for dashboards/monitoring).

## Recommendation
- Wrap the `GET /v2/bridge_types/:BridgeName` route (and any equivalent GraphQL `bridge`/`bridges` resolvers) with `auth.RequiresEditRole` (or a role commensurate with `OutgoingToken`'s sensitivity), matching `Create`/`Update`/`Destroy`.
- Alternatively, redact `OutgoingToken` from `Show`/`Index` responses for non-privileged roles, using the same `omitempty`/creation-only pattern already applied to `IncomingToken` in `presenters.BridgeResource`.
- Audit other `GET` routes in `core/web/router.go` for the same asymmetric-role pattern to catch further secret leaks through underprotected `Show`/`Index` actions.

## Proof of Concept
1. As an admin, create a bridge (capturing its name) and separately create a `View`-role user/API token.
2. Authenticate as the `View`-role user and issue `GET /v2/bridge_types/<bridgeName>`.
3. Observe the JSON response body includes `"outgoingToken": "<secret>"`, confirmed by the RBAC test entry `{"GET", "/v2/bridge_types/MOCK", true, true, true}` in `core/web/auth/auth_test.go` (viewOnlyAllowed=true) and the unconditional `OutgoingToken` field in `core/web/presenters/bridges.go`.

### Citations

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/auth/auth_test.go (L229-229)
```go
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
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
