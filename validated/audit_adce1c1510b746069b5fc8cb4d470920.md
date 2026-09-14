### Title
Unbounded pagination `size` parameter enables admin-authenticated resource-exhaustion DoS across multiple `/v2` list endpoints - (File: core/web/api.go)

### Summary
The pagination parser used by every paginated `/v2` REST endpoint (jobs, bridges, transactions, tx attempts, nodes, chains, external initiators, forwarders) accepts a client-supplied `size` query parameter and only validates that it is a positive integer, without any upper bound. This mirrors the CVE-2025-55128 bug class (uncontrolled resource consumption via unbounded "items per page" from an authenticated admin-facing endpoint), reachable through any authenticated node-API caller with `View`-level access.

### Finding Description
`ParsePaginatedRequest` parses `size`/`page` query parameters and only rejects values `< 1`; there is no maximum cap: [1](#0-0) 

This function is invoked by the generic `paginatedRequest` middleware wrapper used to build handlers for nearly every list endpoint in the node's authenticated `/v2` API group: [2](#0-1) 

Routes wired through this wrapper include `GET /v2/jobs`, `GET /v2/bridge_types`, `GET /v2/tx_attempts`, `GET /v2/transactions`, `GET /v2/pipeline/runs`, `GET /v2/jobs/:ID/runs`, `GET /v2/nodes`, `GET /v2/chains`, `GET /v2/external_initiators`, and `GET /v2/nodes/evm/forwarders`, all requiring only session/token authentication (not `RequiresEditRole`/`RequiresAdminRole`), i.e., accessible to any authenticated node-API user with default/view privileges: [3](#0-2) [4](#0-3) 

A client-supplied `size` value is passed straight to the ORM query (e.g., `FindJobs(ctx, offset, size)`, `BridgeTypes(ctx, offset, size)`, `TransactionsWithAttempts(ctx, offset, size)`), so a request like `?size=999999999` forces the database layer and the JSON marshalling/response-building path to attempt to allocate and serialize an arbitrarily large result set: [5](#0-4) [6](#0-5) [7](#0-6) 

By contrast, the GraphQL resolvers use a bounded default (`PageDefaultLimit = 50`) but similarly place no upper cap on the client-supplied `Limit` value: [8](#0-7) [9](#0-8) 

### Impact Explanation
An authenticated node-API user (any role able to reach `GET` list endpoints — note most of these do not require `RequiresEditRole`/`RequiresAdminRole`, only the base `Authenticate` middleware) can request an extremely large page size, causing the node to attempt to fetch and marshal an unbounded number of rows in memory. This can exhaust memory/CPU and degrade or crash the Chainlink node process, denying service to legitimate node operations (job execution, pipeline runs, tx broadcasting) — a direct availability impact matching CVSS `AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H` of the referenced CVE.

### Likelihood Explanation
Likelihood is moderate-to-high for any deployment that grants API credentials to more than a single fully-trusted admin, since the affected endpoints require only authentication (session cookie or API token), not elevated role checks. The attack requires no special crafting beyond a single query parameter and no state beyond a valid session/token.

### Recommendation
Enforce a maximum allowed `size` (and reject/clamp values above it) in `ParsePaginatedRequest` in `core/web/api.go`, and apply an analogous cap to GraphQL `pageLimit` in `core/web/resolver/helpers.go`. Consider also bounding query timeouts/row-count at the ORM layer as defense in depth.

### Proof of Concept
```
GET /v2/jobs?size=2147483647&page=1 HTTP/1.1
Host: <chainlink-node>
Cookie: <valid session for a non-admin, view-only user>
```
`ParsePaginatedRequest` accepts this value unmodified (only checks `size < 1`), and `JobsController.Index` passes it directly to `FindJobs(ctx, offset, size)`, forcing the ORM/DB layer to attempt to return/marshal the entire jobs table in one response.

### Citations

**File:** core/web/api.go (L32-51)
```go
func ParsePaginatedRequest(sizeParam, pageParam string) (int, int, int, error) {
	var err error
	page := 1
	size := PaginationDefault

	if sizeParam != "" {
		if size, err = strconv.Atoi(sizeParam); err != nil || size < 1 {
			return 0, 0, 0, fmt.Errorf("invalid size param, error: %w", err)
		}
	}

	if pageParam != "" {
		if page, err = strconv.Atoi(pageParam); err != nil || page < 1 {
			return 0, 0, 0, fmt.Errorf("invalid page param, error: %w", err)
		}
	}

	offset := (page - 1) * size
	return size, page, offset, nil
}
```

**File:** core/web/helpers.go (L53-62)
```go
func paginatedRequest(action func(*gin.Context, int, int, int)) func(*gin.Context) {
	return func(c *gin.Context) {
		size, page, offset, err := ParsePaginatedRequest(c.Query("size"), c.Query("page"))
		if err != nil {
			jsonAPIError(c, http.StatusUnprocessableEntity, err)
			return
		}
		action(c, size, page, offset)
	}
}
```

**File:** core/web/router.go (L263-295)
```go
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

		ets := EVMTransfersController{app}
		authv2.POST("/transfers", auth.RequiresAdminRole(ets.Create))
		authv2.POST("/transfers/evm", auth.RequiresAdminRole(ets.Create))
		tts := CosmosTransfersController{app}
		authv2.POST("/transfers/cosmos", auth.RequiresAdminRole(tts.Create))
		sts := SolanaTransfersController{app}
		authv2.POST("/transfers/solana", auth.RequiresAdminRole(sts.Create))

		cc := ConfigController{app}
		authv2.GET("/config", cc.Show)
		authv2.GET("/config/v2", cc.Show)

		tas := TxAttemptsController{app}
		authv2.GET("/tx_attempts", paginatedRequest(tas.Index))
		authv2.GET("/tx_attempts/evm", paginatedRequest(tas.Index))

		txs := TransactionsController{app}
		authv2.GET("/transactions/evm", paginatedRequest(txs.Index))
		authv2.GET("/transactions/evm/:TxHash", txs.Show)
		authv2.GET("/transactions", paginatedRequest(txs.Index))
		authv2.GET("/transactions/:TxHash", txs.Show)
```

**File:** core/web/router.go (L391-431)
```go
		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))

		// PipelineRunsController
		authv2.GET("/pipeline/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs/:runID", prc.Show)

		// FeaturesController
		fc := FeaturesController{app}
		authv2.GET("/features", fc.Index)

		// PipelineJobSpecErrorsController
		authv2.DELETE("/pipeline/job_spec_errors/:ID", auth.RequiresEditRole(psec.Destroy))

		lgc := LogController{app}
		authv2.GET("/log", lgc.Get)
		authv2.PATCH("/log", auth.RequiresAdminRole(lgc.Patch))

		chains := authv2.Group("chains")
		chainController := NewChainsController(
			app.GetRelayers(),
			app.GetLogger(),
			app.GetAuditLogger(),
		)
		chains.GET("", paginatedRequest(chainController.Index))
		chains.GET("/:network", paginatedRequest(chainController.Index))
		chains.GET("/:network/:ID", chainController.Show)

		nodes := authv2.Group("nodes")
		nodesController := NewNodesController(
			app.GetRelayers(),
			app.GetAuditLogger(),
		)
		nodes.GET("", paginatedRequest(nodesController.Index))
		nodes.GET("/:network", paginatedRequest(nodesController.Index))
		chains.GET("/:network/:ID/nodes", paginatedRequest(nodesController.Index))
```

**File:** core/web/jobs_controller.go (L44-61)
```go
func (jc *JobsController) Index(c *gin.Context, size, page, offset int) {
	// Temporary: if no size is passed in, use a large page size. Remove once frontend can handle pagination
	if c.Query("size") == "" {
		size = 1000
	}

	jobs, count, err := jc.App.JobORM().FindJobs(c.Request.Context(), offset, size)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
	var resources []presenters.JobResource
	for _, individualJob := range jobs {
		resources = append(resources, *presenters.NewJobResource(individualJob))
	}

	paginatedResponse(c, "jobs", size, page, resources, count, err)
}
```

**File:** core/web/bridge_types_controller.go (L111-122)
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
```

**File:** core/web/evm_transactions_controller.go (L20-29)
```go
// Index returns paginated transactions
func (tc *TransactionsController) Index(c *gin.Context, size, page, offset int) {
	txs, count, err := tc.App.TxmStorageService().TransactionsWithAttempts(c, offset, size)
	ptxs := make([]presenters.EthTxResource, len(txs))
	for i, tx := range txs {
		tx.TxAttempts[0].Tx = tx
		ptxs[i] = presenters.NewEthTxResourceFromAttempt(tx.TxAttempts[0])
	}
	paginatedResponse(c, "transactions", size, page, ptxs, count, err)
}
```

**File:** core/web/resolver/helpers.go (L17-51)
```go
const (
	// PageDefaultOffset defines the default offset to use if none is provided
	PageDefaultOffset = 0

	// PageDefaultLimit defines the default limit to use if none is provided
	PageDefaultLimit = 50
)

func int32GQLID(i int32) graphql.ID {
	return graphql.ID(stringutils.FromInt32(i))
}

func int64GQLID(i int64) graphql.ID {
	return graphql.ID(stringutils.FromInt64(i))
}

// pageOffset returns the default page offset if nil, otherwise it returns the
// provided offset.
func pageOffset(offset *int32) int {
	if offset == nil {
		return PageDefaultOffset
	}

	return int(*offset)
}

// pageLimit returns the default page limit if nil, otherwise it returns the
// provided limit.
func pageLimit(limit *int32) int {
	if limit == nil {
		return PageDefaultLimit
	}

	return int(*limit)
}
```

**File:** core/web/resolver/query.go (L50-68)
```go
// Bridges retrieves a paginated list of bridges.
func (r *Resolver) Bridges(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*BridgesPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)

	brdgs, count, err := r.App.BridgeORM().BridgeTypes(ctx, offset, limit)
	if err != nil {
		return nil, err
	}

	return NewBridgesPayload(brdgs, safeInt32(count)), nil
}
```
