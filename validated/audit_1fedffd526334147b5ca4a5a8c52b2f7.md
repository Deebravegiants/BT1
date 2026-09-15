This confirms the router explicitly defines a `UserRoleView` tier (lowest privilege, distinct from `run`, `edit`, `admin`), and `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` middleware all specifically block `UserRoleView` from performing writes/runs. But the bridge read routes — `authv2.GET("/bridge_types", paginatedRequest(bt.Index))` and `authv2.GET("/bridge_types/:BridgeName", bt.Show)` — are registered with **no role-check wrapper at all**, only the base `authv2` group's `auth.Authenticate` (session/token). This means a `UserRoleView` user (the lowest role in the system, intended for read-only dashboard access) can invoke these endpoints and receive the full `OutgoingToken` in the response, confirming the report's central open question. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

Note: the GraphQL `/query` endpoint uses `auth.AuthenticateGQL` (session/token authentication only, no per-field role gating visible in `resolver/bridge.go`), so the same low-privilege read exposure applies there too, consistent with the test fixtures showing `outgoingToken` always present in `bridge`/`bridges` query results.

Audit Report

## Title
Bridge `OutgoingToken` secret is disclosed to view-role (lowest-privilege) authenticated users via unguarded read endpoints - (File: `core/web/presenters/bridges.go`)

## Summary
`BridgeResource.OutgoingToken` (`core/web/presenters/bridges.go:17`) has no `omitempty`/redaction, unlike `IncomingToken`, and is unconditionally populated by `NewBridgeResource` on every read. The `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` routes are registered in `core/web/router.go` with no role-restriction wrapper (unlike the mutating bridge routes, which use `auth.RequiresEditRole`), so any authenticated user — including the lowest-privilege `UserRoleView` role — can retrieve the live outgoing secret for every configured bridge.

## Finding Description
`BridgeType.OutgoingToken` is a plaintext secret stored in `bridge_types` used to let an external adapter verify inbound calls from the node. `NewBridgeResource` copies it unconditionally into the JSON:API response:
```go
OutgoingToken string `json:"outgoingToken"`
```
while `IncomingToken` is deliberately `json:"incomingToken,omitempty"` and set only transiently in `BridgeTypesController.Create`. This asymmetry is the root cause: `OutgoingToken` was never given the same write-once/redact-on-read treatment.

Critically, the route registration for the read endpoints has no role gate:
```go
authv2.GET("/bridge_types", paginatedRequest(bt.Index))
authv2.GET("/bridge_types/:BridgeName", bt.Show)
```
Compare this to the mutating endpoints on the same lines, which are explicitly wrapped with `auth.RequiresEditRole`. The `authv2` group only requires generic authentication (`auth.AuthenticateByToken`/`auth.AuthenticateBySession`), with no minimum role check for these two GET handlers. Chainlink's own role model (`core/web/auth/auth.go`) defines a `UserRoleView` explicitly intended to be lower-privileged than `run`/`edit`/`admin` — `RequiresRunRole` and `RequiresEditRole` both explicitly reject `UserRoleView`. Since `bt.Index`/`bt.Show` bypass those checks entirely, a `UserRoleView` account (a legitimate, lower-privilege credential tier that exists specifically to prevent write/run access) can still fully read every bridge's `OutgoingToken`. The equivalent GraphQL `bridge`/`bridges` resolvers (`core/web/resolver/bridge.go`) expose the same field with no additional field-level authorization beyond the base authenticated-session check.

## Impact Explanation
This is a genuine least-privilege violation: a viewer-role credential, which per the code's own role hierarchy should not be trusted with mutation or run capability, can still exfiltrate a secret (`OutgoingToken`) intended to authenticate the node's outbound calls to external adapters. Possessing this secret lets the viewer impersonate legitimate node-to-adapter traffic for the corresponding bridge/external adapter, which maps to Chainlink's in-scope "key/secret exfiltration" impact class. Severity is bounded by the fact that exploitation still requires a valid, provisioned account on the node (even if low-privilege) — it is not exploitable by a fully unauthenticated actor.

## Likelihood Explanation
High, for any deployment that provisions `view`-role accounts (a supported, documented role tier) for dashboards/monitoring/read-only access. Any such account can call `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` (or the GraphQL equivalents) with no additional guard, and the secret is returned in the normal, expected response body — no exotic exploit chain, timing, or race condition is required.

## Recommendation
Add role gating consistent with the rest of the bridge routes, e.g. wrap `bt.Index`/`bt.Show` with at least `auth.RequiresEditRole` (or a dedicated check excluding `UserRoleView`) if the token must remain readable at all; better, apply the same `omitempty`/write-once redaction already used for `IncomingToken` to `OutgoingToken` in `BridgeResource` and `BridgeResolver.OutgoingToken()`, only exposing it once at creation time, and rotate/hash it so raw disclosure is not needed for verification.

## Proof of Concept
1. As an admin, create a bridge via `POST /v2/bridge_types` → response includes `outgoingToken`.
2. Create/obtain a session or API token for a user with `UserRoleView` (`core/sessions` role `view`).
3. As that `view`-role user, call `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` — observe the same `outgoingToken` value is returned, per the presenter logic in `core/web/presenters/bridges.go:17-21` and confirmed by the unguarded route registration in `core/web/router.go:269-271` (no `auth.RequiresEditRole`/`auth.RequiresRunRole` wrapper, unlike lines 270/272/273 for POST/PATCH/DELETE).
4. Equivalently, issue the GraphQL query `{ bridges { results { outgoingToken } } }` as the same `view`-role session and confirm the same field is returned, per `core/web/resolver/bridge.go:52-55` and the existing test fixtures in `core/web/resolver/bridge_test.go`.

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

**File:** core/web/presenters/bridges.go (L10-21)
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
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
}
```

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
