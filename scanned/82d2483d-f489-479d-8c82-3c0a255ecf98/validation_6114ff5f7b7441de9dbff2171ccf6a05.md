### Title
Missing role check on Bridge Type `Show` endpoint discloses external adapter URL/config to low-privileged users - (File: core/web/router.go)

### Summary
The `/v2/bridge_types/:BridgeName` `GET` route (`BridgeTypesController.Show`) is registered with no role restriction, while the sibling `Create`, `Update`, and `Destroy` routes for the same resource explicitly require `auth.RequiresEditRole`. Any authenticated user with the lowest privilege (`UserRoleView`) can call this endpoint and retrieve the bridge's configured external adapter URL and other bridge metadata that should only be visible/manageable by Edit-level users.

### Finding Description
In the route table, bridge type mutation endpoints are protected with `auth.RequiresEditRole`, but `Show` is not: [1](#0-0) 

`BridgeTypesController.Show` performs no additional authorization check beyond the base `Authenticate` middleware applied to the whole `authv2` group (token or session auth, any role): [2](#0-1) [3](#0-2) 

`Show` returns a `presenters.BridgeResource`, which is built directly from the stored `bridges.BridgeType`, including its configured `URL` (the external adapter endpoint the node connects to when running jobs that use the bridge) — the same object whose creation/update is gated behind Edit role because it represents outbound-connection configuration: [4](#0-3) 

This mirrors the structure of the reported bug class: a resource whose *mutation* actions correctly enforce a stronger permission, but whose *read* action is reachable by an actor with a much weaker permission level, exposing connection details (URL/target) tied to a specific credential/bridge identifier obtained independently (e.g., via `GET /v2/bridge_types` `Index`, which is also unauthenticated-by-role): [5](#0-4) 

### Impact Explanation
Bridge URLs frequently encode operator-managed endpoint/credential information for external adapters (basic auth in the URL, internal-network hostnames, etc.). A low-privileged (View-role) authenticated user can enumerate bridges via `Index` and then read full URL details via `Show`, without needing the Edit permission the system otherwise requires for accessing/managing this data. This is a confidentiality impact consistent with CWE-285/CWE-862 (missing/incorrect authorization) analogous to the reported Jenkins plugin issue, where a low-privilege actor could retrieve connection/credential information intended to require a higher permission level.

### Likelihood Explanation
High: the endpoint is reachable via a single authenticated HTTP `GET` request; only a valid session or API token of the lowest role is required. No other node compromise or special conditions are needed.

### Recommendation
Add `auth.RequiresEditRole` (or the same role required for `Index`/mutation routes, consistently) to `authv2.GET("/bridge_types/:BridgeName", bt.Show)` in `core/web/router.go`, matching the protection level of `Create`, `Update`, and `Destroy`. Also review whether `BridgeResource` should redact the `URL` field for viewer-role requests if broader read access is intentionally retained for other reasons.

### Proof of Concept
1. Create a session/API token for a user with role `View` only.
2. As an Edit/Admin user, create a bridge: `POST /v2/bridge_types` with `{"name":"mybridge","url":"http://internal-adapter.internal/secret-path?key=..."}`.
3. As the View-role user, call `GET /v2/bridge_types/mybridge`.
4. Observe the response includes the full bridge `URL`, even though the View-role user is not authorized to create/update/delete bridges — demonstrating the read-path permission gap.

Note: I could not fully inspect `core/web/presenters/bridges.go` to confirm every field serialized in `BridgeResource` (e.g., whether `URL` is unconditionally included) due to index/content limits; this should be verified directly in the repo if deeper confirmation of the exact serialized fields is needed.

### Citations

**File:** core/web/router.go (L245-273)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	{
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)

		wa := NewWebAuthnController(app)
		authv2.GET("/enroll_webauthn", wa.BeginRegistration)
		authv2.POST("/enroll_webauthn", wa.FinishRegistration)

		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))

		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/bridge_types_controller.go (L60-109)
```go
// Create adds the BridgeType to the given context.
func (btc *BridgeTypesController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	btr := &bridges.BridgeTypeRequest{}

	if err := c.ShouldBindJSON(btr); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
	bta, bt, err := bridges.NewBridgeType(btr)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
	if e := ValidateBridgeType(btr); e != nil {
		jsonAPIError(c, http.StatusBadRequest, e)
		return
	}
	orm := btc.App.BridgeORM()
	if e := ValidateBridgeTypeNotExist(ctx, btr, orm); e != nil {
		jsonAPIError(c, http.StatusBadRequest, e)
		return
	}
	if e := orm.CreateBridgeType(ctx, bt); e != nil {
		jsonAPIError(c, http.StatusInternalServerError, e)
		return
	}
	var pgErr *pgconn.PgError
	if errors.As(err, &pgErr) {
		var apiErr error
		if pgErr.ConstraintName == "external_initiators_name_key" {
			apiErr = fmt.Errorf("bridge Type %v conflict", bt.Name)
		} else {
			apiErr = err
		}
		jsonAPIError(c, http.StatusConflict, apiErr)
		return
	}
	resource := presenters.NewBridgeResource(*bt)
	resource.IncomingToken = bta.IncomingToken

	btc.App.GetAuditLogger().Audit(audit.BridgeCreated, map[string]any{
		"bridgeName":                   bta.Name,
		"bridgeConfirmations":          bta.Confirmations,
		"bridgeMinimumContractPayment": bta.MinimumContractPayment,
		"bridgeURL":                    bta.URL,
	})

	jsonAPIResponse(c, resource, "bridge")
}
```

**File:** core/web/bridge_types_controller.go (L124-146)
```go
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
