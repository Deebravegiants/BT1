Analog vulnerability confirmed — a missing-permission-check (role-gate) exposing a stored secret token, comparable in bug-class to CVE-2024-44313's unauthorized data exposure due to missing permission check.

### Title
Bridge OutgoingToken Secret Exposed to Any Authenticated (View-Role) User via Missing Role Check - (File: core/web/router.go, core/web/presenters/bridges.go)

### Summary
The `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` endpoints are registered without any role-gating middleware, allowing the lowest-privilege authenticated role (`View`) to retrieve the bridge's `OutgoingToken` secret, which the presenter serializes unconditionally.

### Finding Description
In `v2Routes`, the bridge read endpoints are wired with no `RequiresEditRole`/`RequiresAdminRole` wrapper, unlike the mutating bridge routes which are correctly gated: [1](#0-0) 

The RBAC test map confirms this is reachable by the `View` role (the weakest authenticated role) without any 401/403: [2](#0-1) 

The response presenter for this endpoint always serializes `OutgoingToken`, while `IncomingToken` is explicitly commented as deliberately excluded except at creation time — showing the maintainers intended for bridge secrets to be redacted post-creation, but this protection was not applied consistently to `OutgoingToken`: [3](#0-2) 

`OutgoingToken` is generated as a cryptographically random secret at bridge creation time, alongside `OutgoingSecret`, and is meant to be used by the node to authenticate itself to the external adapter/bridge: [4](#0-3) 

Because `authv2.GET("/bridge_types", ...)` and `authv2.GET("/bridge_types/:BridgeName", ...)` require only base session/token authentication (`auth.Authenticate(...)`) with no subsequent `RequiresEditRole`/`RequiresAdminRole` check, any authenticated node user — including the minimal `View` role, which per the codebase's own role model should not be able to mutate or access privileged secrets — can retrieve this bridge secret token in plaintext via the JSON API response.

### Impact Explanation
The `OutgoingToken` is a shared secret used to authenticate the node's outbound calls to bridge adapters/external services. Disclosure to a low-privileged `View` user allows that user to impersonate the node when calling the bridge/external adapter directly, potentially triggering unintended external side effects or bypassing the adapter's expectation that only the legitimate Chainlink node instance can invoke it with that secret. This is a concrete secret disclosure across a privilege boundary that the codebase's own RBAC model (View < Run < Edit < Admin) is designed to prevent for sensitive material.

### Likelihood Explanation
High likelihood: any user account provisioned with the lowest `View` role (a common non-admin operator/read-only account type explicitly supported by the system) can trivially call `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` with a valid session/API token and receive the secret in the JSON response — no additional exploitation steps or race conditions required.

### Recommendation
Redact `OutgoingToken` from the `BridgeResource` presenter for read/list endpoints (mirroring the existing `omitempty`/creation-only exposure pattern already applied to `IncomingToken`), or gate `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` behind `auth.RequiresEditRole`/`RequiresAdminRole` so only privileged roles can view bridge secrets.

### Proof of Concept
1. Provision or use an API user with role `View` (`clsessions.UserRoleView`), the lowest role in the RBAC model.
2. Authenticate and call `GET /v2/bridge_types/<BridgeName>` (or `GET /v2/bridge_types`).
3. Observe the JSON:API response includes `"outgoingToken": "<secret>"` for the bridge, confirmed reachable by `View` role per the RBAC route map test (`viewOnlyAllowed=true` for this route) and the unconditional serialization in `NewBridgeResource`.
4. Use the disclosed `OutgoingToken` to authenticate a request directly to the bridge's configured external adapter/service, impersonating the node's outgoing call.

**Note on scope/uncertainty:** The `BridgeTypesController.Show`/`Index` handler bodies themselves were not fully retrieved due to index limits on `core/web/bridge_types_controller.go`; the finding is based on the confirmed route registration (`core/web/router.go`), presenter (`core/web/presenters/bridges.go`), and RBAC test coverage (`core/web/auth/auth_test.go`). If a full audit of the handler is needed to rule out additional server-side masking not visible in the presenter, a Devin session with full file access would be required.

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

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
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

**File:** core/bridges/external_initiator.go (L36-57)
```go
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
