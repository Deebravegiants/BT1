### Title
Unbounded pagination `size`/`limit` parameters allow authenticated low-privilege users to trigger denial of service - ([File: core/web/api.go])

### Summary
Chainlink's REST and GraphQL list endpoints accept client-controlled `size`/`limit` parameters for pagination but never enforce an upper bound, mirroring the aim CVE-2024-12778 root cause (no limit on the number of records that can be requested per call). Any authenticated user — including one holding only the low-privilege `view` role — can request an arbitrarily large page of jobs, pipeline runs, ETH transactions, or bridges in a single call, forcing the node to load and marshal the entire result set into memory and JSON, which can exhaust CPU/memory and stall the web server for all other users.

### Finding Description
`ParsePaginatedRequest` in `core/web/api.go` validates that `size` is a positive integer but places no ceiling on it: `if size, err = strconv.Atoi(sizeParam); err != nil || size < 1 { ... }` [1](#0-0) . This function backs the `paginatedRequest` wrapper used by numerous REST controllers via `core/web/router.go` and `core/web/helpers.go` [2](#0-1) .

Controllers such as `JobsController.Index` and `PipelineRunsController.Index` even override the client-supplied default with a large hardcoded page size (1000) "temporarily," but a user can still explicitly pass an arbitrarily large `size` query parameter (e.g. `?size=100000000`) since no maximum is enforced: [3](#0-2) [4](#0-3) .

The same pattern exists in the GraphQL resolver layer: `pageLimit`/`pageOffset` simply cast the client-supplied `*int32` to `int` with no cap, and this feeds directly into ORM queries for jobs, bridges, ETH transactions, and node lists: [5](#0-4) . Examples of resolvers using these unbounded values include `Bridges`, `Jobs`, `Nodes`, `JobRuns`, `EthTransactions`, and `EthTransactionsAttempts` — each simply forwards `offset`/`limit` straight to the ORM layer: [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) .

All of these routes sit behind session/API-key authentication and a generic rate limiter (`rateLimiter` middleware and `AuthenticateGQL`), but the rate limiter only throttles request *frequency*, not the *cost* of an individual request: [10](#0-9) . A single low-cost request with a huge `size`/`limit` value can still force the ORM to fetch and the JSON/JSONAPI marshaller to serialize an enormous result set in one shot, which is exactly the aim DoS pattern (single-threaded/blocking server + no per-call limit on retrieved records).

### Impact Explanation
Because the node's HTTP web server handles requests in Gin's goroutine-per-request model but shares a single database connection pool and CPU-bound JSON marshalling path, a single oversized paginated request (e.g. jobs, pipeline runs, ETH transactions, or GraphQL `nodes`/`jobRuns`/`ethTransactions` queries) can consume excessive memory and CPU, and hold database connections/locks long enough to degrade or block the operator UI and other legitimate authenticated requests — a denial of service directly analogous to the aim CVE. This does not require any privileged (`admin`) role, only a valid low-privilege authenticated session or API token, which the rules classify as within scope (unprivileged-actor path via authenticated user API).

### Likelihood Explanation
Any authenticated user, including those provisioned with the minimal `view` role over the node's UI/API, can trigger this by adding a large `size`/`limit`/`page` parameter to any of the many endpoints backed by `ParsePaginatedRequest` or `pageLimit`/`pageOffset`. No special timing, race conditions, or privileged access is required — a single crafted GET or GraphQL POST request suffices.

### Recommendation
Enforce a hard maximum on `size`/`limit` in `ParsePaginatedRequest` (`core/web/api.go`) and in `pageLimit` (`core/web/resolver/helpers.go`), rejecting or clamping values above a sane ceiling (e.g. 1000), and audit all controllers/resolvers that bypass this default (like the `size == "" → 1000` override in `JobsController`/`PipelineRunsController`) to ensure they cannot be overridden to unbounded values by client input.

### Proof of Concept
Against a running chainlink node with a valid low-privilege session cookie/API token:
```
GET /v2/jobs?size=100000000&page=1
```
or via GraphQL:
```
POST /query
{"query": "{ jobs(offset: 0, limit: 2000000000) { results { id } } }"}
```
Both requests pass validation in `ParsePaginatedRequest`/`pageLimit` (which only rejects `size < 1`, not oversized values) and are forwarded unmodified to the ORM layer (`FindJobs`, `PipelineRuns`, etc.), causing the node to attempt to load and serialize an outsized result set.

### Citations

**File:** core/web/api.go (L37-41)
```go
	if sizeParam != "" {
		if size, err = strconv.Atoi(sizeParam); err != nil || size < 1 {
			return 0, 0, 0, fmt.Errorf("invalid size param, error: %w", err)
		}
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

**File:** core/web/jobs_controller.go (L44-60)
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
```

**File:** core/web/pipeline_runs_controller.go (L26-61)
```go
// Index returns all pipeline runs for a job.
// Example:
// "GET <application>/jobs/:ID/runs"
func (prc *PipelineRunsController) Index(c *gin.Context, size, page, offset int) {
	id := c.Param("ID")

	// Temporary: if no size is passed in, use a large page size. Remove once frontend can handle pagination
	if c.Query("size") == "" {
		size = 1000
	}

	var pipelineRuns []pipeline.Run
	var count int
	var err error

	ctx := c.Request.Context()
	if id == "" {
		pipelineRuns, count, err = prc.App.JobORM().PipelineRuns(ctx, nil, offset, size)
	} else {
		jobSpec := job.Job{}
		err = jobSpec.SetID(c.Param("ID"))
		if err != nil {
			jsonAPIError(c, http.StatusUnprocessableEntity, err)
			return
		}

		pipelineRuns, count, err = prc.App.JobORM().PipelineRuns(ctx, &jobSpec.ID, offset, size)
	}

	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	res := presenters.NewPipelineRunResources(pipelineRuns, prc.App.GetLogger())
	paginatedResponse(c, "pipelineRun", size, page, res, count, err)
```

**File:** core/web/resolver/helpers.go (L43-51)
```go
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

**File:** core/web/resolver/query.go (L234-252)
```go
// Jobs fetches a paginated list of jobs
func (r *Resolver) Jobs(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*JobsPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)

	jobs, count, err := r.App.JobORM().FindJobs(ctx, offset, limit)
	if err != nil {
		return nil, err
	}

	return NewJobsPayload(r.App, jobs, safeInt32(count)), nil
}
```

**File:** core/web/resolver/query.go (L389-413)
```go
// Nodes retrieves a paginated list of nodes.
func (r *Resolver) Nodes(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*NodesPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)
	r.App.GetLogger().Debugw("resolver Nodes query", "offset", offset, "limit", limit)
	allNodes, total, err := r.App.GetRelayers().NodeStatuses(ctx, offset, limit)
	r.App.GetLogger().Debugw("resolver Nodes query result", "nodes", allNodes, "total", total, "err", err)

	if err != nil {
		r.App.GetLogger().Errorw("Error creating get nodes status from app", "err", err)
		return nil, err
	}
	npr, warn := NewNodesPayload(allNodes, safeInt32(total))
	if warn != nil {
		r.App.GetLogger().Warnw("Error creating NodesPayloadResolver", "err", warn)
	}
	return npr, nil
}
```

**File:** core/web/resolver/query.go (L536-572)
```go
func (r *Resolver) EthTransactions(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*EthTransactionsPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)

	txs, count, err := r.App.TxmStorageService().Transactions(ctx, offset, limit)
	if err != nil {
		return nil, err
	}

	return NewEthTransactionsPayload(txs, safeInt32(count)), nil
}

func (r *Resolver) EthTransactionsAttempts(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*EthTransactionsAttemptsPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)

	attempts, count, err := r.App.TxmStorageService().TxAttempts(ctx, offset, limit)
	if err != nil {
		return nil, err
	}

	return NewEthTransactionsAttemptsPayload(attempts, safeInt32(count)), nil
}
```

**File:** core/web/router.go (L77-99)
```go
	rl := config.WebServer().RateLimit()
	api := engine.Group(
		"/",
		rateLimiter(
			rl.AuthenticatedPeriod(),
			rl.Authenticated(),
		),
		sessions.Sessions(auth.SessionName, sessionStore),
	)

	debugRoutes(app, api)
	healthRoutes(app, api)
	sessionRoutes(app, api)
	v2Routes(app, api)
	loopRoutes(app, api)

	guiAssetRoutes(engine, config.Insecure().DisableRateLimiting(), app.GetLogger())

	api.POST("/query",
		auth.AuthenticateGQL(app.AuthenticationProvider(), app.GetLogger().Named("GQLHandler")),
		loader.Middleware(app),
		graphqlHandler(app),
	)
```
