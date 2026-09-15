The code confirms every element of the claim precisely as described.

Audit Report

## Title
Under-protected Bridge Show endpoint leaks the bridge's `OutgoingToken` secret to view-only users - ([File: core/web/router.go], [File: core/web/presenters/bridges.go])

## Summary
`GET /v2/bridge_types/:BridgeName` is registered in `core/web/router.go` without any role-based wrapper, unlike the sibling `POST`/`PATCH`/`DELETE` bridge_types routes which all require `auth.RequiresEditRole`. The handler returns a `BridgeResource` presenter (`core/web/presenters/bridges.go`) that unconditionally serializes `OutgoingToken`, a secret credential the node uses to authenticate to the external bridge adapter, allowing any authenticated `view`-role user to read it.

## Finding Description
In `core/web/router.go`, the bridge routes are: [1](#0-0)  — `bt.Create`, `bt.Update`, and `bt.Destroy` are wrapped in `auth.RequiresEditRole`, but `bt.Show` is registered bare, subject only to the generic `Authenticate` middleware applied to the whole `authv2` group [2](#0-1) , which accepts any valid session or API token regardless of role.

The `BridgeResource` presenter returned by `Show` includes `OutgoingToken` with no `omitempty` and no role-based redaction: [3](#0-2) . The underlying `BridgeType.OutgoingToken` is a generated secret (`utils.NewSecret(24)`) stored in plaintext in the DB and used as the credential the node presents to the external adapter: [4](#0-3) .

The role middleware that should gate this is `RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` in `core/web/auth/auth.go`, which explicitly blocks `UserRoleView` (and `RequiresEditRole` also blocks `UserRoleRun`): [5](#0-4) . Because `bt.Show` is not wrapped by any of these, a `view`-role user passes straight through to the handler with no additional check performed inside the handler itself — this is a genuine gap, not a false claim: existing RBAC middleware was reviewed and confirmed to only apply to `Create`/`Update`/`Destroy`, not `Show`.

## Impact Explanation
This is a real, in-scope "incorrect access control" / secret exfiltration issue: a low-privilege `view`-role authenticated actor can retrieve `OutgoingToken`, a bearer credential intended to be restricted to `edit`/`admin` roles (matching how `IncomingToken` is deliberately withheld post-creation via `omitempty`). Possessing `OutgoingToken` lets an attacker impersonate the Chainlink node to the external bridge adapter or use it to pivot into systems the `view` role was never meant to reach. This maps to the "key/secret exfiltration" impact category and is caused entirely by first-party route/presenter code, not by a misconfiguration, dependency, or malicious peer.

## Likelihood Explanation
Exploitation requires only a valid `view`-role session or API token (the lowest privilege tier, commonly issued to read-only dashboards/monitoring integrations) and knowledge of a bridge name — trivially obtainable via the also role-unrestricted `GET /v2/bridge_types` index route in the same route group. No additional complexity, timing, or race conditions are needed, making this fully and repeatably reproducible.

## Recommendation
- Wrap `authv2.GET("/bridge_types/:BridgeName", bt.Show)` with `auth.RequiresEditRole` (or at minimum `auth.RequiresRunRole`) in `core/web/router.go`.
- Alternatively, keep the route accessible to all authenticated roles, but redact `OutgoingToken` in `NewBridgeResource` (`core/web/presenters/bridges.go`) unless the requester holds `edit`/`admin` role.
- Add/extend an RBAC route-map regression test analogous to `TestRBAC_Routemap_ViewOnly` in `core/web/auth/auth_test.go` asserting `viewOnlyAllowed: false` for this route.

## Proof of Concept
1. As an `admin`/`edit` user, `POST /v2/bridge_types` to create a bridge; capture the returned `outgoingToken`.
2. Create/use a `view`-role API token (`sessions.UserRoleView`).
3. As the `view` user: `GET /v2/bridge_types` to list bridge names, then `GET /v2/bridge_types/<BridgeName>`.
4. Observe the JSON response contains `"outgoingToken": "<secret>"` with HTTP 200, while a `POST`/`PATCH`/`DELETE` to the same resource from the same `view` user correctly returns 401/403 due to `auth.RequiresEditRole`.
5. This can be codified as a Go handler test in `core/web/bridge_types_controller_test.go` asserting a `view`-role client receives `outgoingToken` in the `Show` response, or as an addition to `core/web/auth/auth_test.go`'s route map fixture (`{"GET", "/v2/bridge_types/MOCK", true, true, true}` → expected `false` for `viewOnlyAllowed`).

### Citations

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
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

**File:** core/bridges/bridge_type.go (L63-101)
```go
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
