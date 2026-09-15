### Title
View-role users can read bridge adapter outgoing authentication tokens via unrestricted `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` - (File: core/web/router.go)

### Summary
The bridge type read endpoints (`Index`/`Show`) are registered without any role-based middleware, so any authenticated user — including the lowest-privilege `view` role — can retrieve the `OutgoingToken` secret used to authenticate the node to external bridge adapters, while mutation endpoints on the same resource correctly require the `edit` role.

### Finding Description
In `core/web/router.go`, the bridge type routes are wired as: [1](#0-0) 

`GET /bridge_types` and `GET /bridge_types/:BridgeName` are only wrapped by the generic `authv2` group (session/token authentication), not by `auth.RequiresEditRole` like `Create`, `Update`, and `Destroy` are. This means any authenticated `view`-role user can call these endpoints.

The handlers for `Index` and `Show` in `core/web/bridge_types_controller.go` build the response directly from `presenters.NewBridgeResource`: [2](#0-1) 

The `BridgeResource` presenter serializes `OutgoingToken` unconditionally (no `omitempty`), unlike `IncomingToken` which is intentionally hidden after creation: [3](#0-2) 

The test suite documents this behavior as intended (`viewOnlyAllowed: true` for both `GET /v2/bridge_types` and `GET /v2/bridge_types/MOCK`, while write operations require `EditAllowed`): [4](#0-3) 

The `OutgoingToken` is the credential the Chainlink node itself uses to authenticate to the configured bridge/external adapter (analogous to a protected-environment secret in the GitLab CVE, where an insufficiently-privileged role could reach data/actions meant to be gated to a higher-trust role). Exposing it to `view` role breaks the intended RBAC boundary between read-only and edit-capable roles for this resource.

### Impact Explanation
A user provisioned with only the `view` role (e.g., an auditor/read-only dashboard account) can extract the `OutgoingToken` for any configured bridge. With that secret, they could impersonate the node when calling the external adapter (if the adapter uses the outgoing token to authorize callbacks/requests), or use it to correlate/replay traffic — capabilities that should be restricted to `edit`/`admin` roles who manage bridge configuration.

### Likelihood Explanation
Any authenticated user with the lowest privilege role can trigger this with a simple `GET` request; no additional bypass or race condition is required, and the RBAC test suite confirms the endpoint is reachable by `view` role as designed. This makes exploitation trivial for any account provisioned at `view` level.

### Recommendation
Add `auth.RequiresEditRole` (or a role check inside the handler) to the `GET /bridge_types` and `GET /bridge_types/:BridgeName` routes, or omit `OutgoingToken` from the presenter response for callers below `edit` role, mirroring the treatment already given to `IncomingToken`.

### Proof of Concept
1. Provision or obtain a session/API token for a user with `Role: view`.
2. Send `GET /v2/bridge_types/<bridgeName>` (or `GET /v2/bridge_types` for all bridges) using that session/token.
3. Observe the JSON:API response includes the `outgoingToken` attribute in `BridgeResource`, despite the requester lacking `edit`/`admin` privileges.

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

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```
