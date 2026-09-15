### Title
Bridge Adapter `OutgoingToken` disclosed to unprivileged Viewer role - (File: core/web/presenters/bridges.go)

### Summary
Chainlink's Bridge management API exposes the `OutgoingToken` credential in the `BridgeResource` JSON representation returned by `GET /v2/bridge_types` (index) and `GET /v2/bridge_types/:BridgeName` (show), and both endpoints are accessible to users holding only the `view` role. This is directly analogous to the Grafana DingDing advisory (GHSA-46m5-8hpj-p5p5), where an integration secret intended to be restricted to Editor/Admin users was inadvertently exposed to Viewer-permission users via the alerting API.

### Finding Description
`BridgeResource` marshals the `OutgoingToken` field without redaction and without an `omitempty`/write-only guard, unlike `IncomingToken` which is explicitly commented as "only provided when creating a Bridge" and is `omitempty`: [1](#0-0) 

`NewBridgeResource` populates `OutgoingToken` directly from the stored `bridges.BridgeType.OutgoingToken` for every response: [2](#0-1) 

The `Index` and `Show` handlers on `BridgeTypesController` both call `presenters.NewBridgeResource(bridge)` and return it without any field-level restriction based on role: [3](#0-2) 

These two routes are registered without any `auth.RequiresEditRole`/`auth.RequiresAdminRole` wrapper, in contrast to `Create`, `Update`, and `Destroy` which are gated behind `auth.RequiresEditRole`: [4](#0-3) 

The project's own RBAC route test matrix confirms this is reachable by the `view` role (`viewOnlyAllowed=true` for both `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName`): [5](#0-4) 

`OutgoingToken` is a per-bridge secret generated alongside `IncomingToken` at bridge creation time via `utils.NewSecret(24)`: [6](#0-5) 

The design intent that `IncomingToken`/credential-like tokens should not be freely re-exposed is evident from the explicit `omitempty` + comment on `IncomingToken` in the same struct; `OutgoingToken` was not given the same treatment, so it leaks on every listing/show call regardless of caller role.

### Impact Explanation
`OutgoingToken` is a credential associated with the external-adapter/bridge integration (structurally identical in purpose to `IncomingToken`, which is deliberately restricted to bridge-creation responses only). Exposing it to any authenticated user — including the least-privileged `view` role, which should only be able to observe non-sensitive node state — violates the principle of least privilege and matches CWE-200 (information exposure) in the same manner as the Grafana DingDing advisory: a secret meant for privileged (Editor/Admin) integration configuration is readable by Viewer-level accounts. Depending on how downstream/external-adapter systems trust this token, disclosure could enable an unprivileged Chainlink node user to impersonate the node's outbound bridge traffic or otherwise misuse the credential outside the intended trust boundary.

### Likelihood Explanation
Likelihood is high for any deployment that grants `view`-role API/UI access to less-trusted operators (a supported and common configuration, as evidenced by the dedicated RBAC role model with `admin`/`edit`/`run`/`view`). No special conditions are needed beyond calling the always-available, unauthenticated-role-gated `GET /v2/bridge_types` or `GET /v2/bridge_types/:BridgeName` endpoints with valid `view` credentials.

### Recommendation
Apply the same restriction used for `IncomingToken` to `OutgoingToken`: mark it `omitempty` and only populate it in the bridge-creation (`Create`) response, or gate the `Index`/`Show` bridge routes with `auth.RequiresEditRole` (or strip the field when the requester is `view`/`run` role) so that only privileged users can retrieve this credential during subsequent reads.

### Proof of Concept
1. As an admin, create a bridge: `POST /v2/bridge_types` with `{"name":"test","url":"http://adapter.local"}` → response includes `outgoingToken`.
2. Create a session/API token for a user with `Role: view` (per `core/sessions` RBAC model).
3. As that `view` user, call `GET /v2/bridge_types/test` (or `GET /v2/bridge_types`).
4. Observe the response JSON contains the same `outgoingToken` value returned at creation time, confirming disclosure to a Viewer-role, unprivileged account — see `core/web/presenters/bridges.go:18` (`OutgoingToken` lacking `omitempty`) and the unrestricted route registration in `core/web/router.go:269,271` compared against `core/web/auth/auth_test.go:227-231` confirming `view` access is permitted.

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

**File:** core/web/bridge_types_controller.go (L112-146)
```go
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

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/bridges/bridge_type.go (L72-102)
```go
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
