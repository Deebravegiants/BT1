## Analysis

The Elasticsearch CVE describes an authenticated, read-only user submitting a small request whose size/count field is used unchecked to drive a large server-side memory allocation. The closest analog in this repo is the GraphQL pagination path for job runs, bridges, and nodes, where the client-supplied `Limit` argument is converted directly to an `int` and passed to the ORM query with no upper-bound validation.

### Title
Unbounded GraphQL `Limit` Argument Enables Memory-Exhaustion Denial of Service - (File: core/web/resolver/helpers.go)

### Summary
The GraphQL resolvers `JobRuns`, `Bridges`, and `Nodes` accept a client-controlled `Limit` argument that is passed through `pageLimit()` with no maximum-value check, then forwarded to database/ORM calls that allocate result slices sized to that value.

### Finding Description
`pageLimit()` only substitutes a default (`PageDefaultLimit = 50`) when `Limit` is `nil`; any other value, including `math.MaxInt32`, is returned unmodified: [1](#0-0) . This value flows straight into `r.App.JobORM().PipelineRuns(ctx, nil, offset, limit)` in the `JobRuns` resolver: [2](#0-1) , and analogously into `BridgeTypes` and `NodeStatuses` for `Bridges`/`Nodes`: [3](#0-2) [4](#0-3) . Unlike the `size` parameter on the REST pagination path (`ParsePaginatedRequest`), which only validates for parse errors and negative/zero values but likewise has no upper bound: [5](#0-4) , none of these paths clamp the value against a maximum. The only gate before reaching these resolvers is `authenticateUser(ctx)`, which requires just an authenticated session, not any elevated role: [6](#0-5) .

This mirrors the CWE-789 pattern in the report: a single small request (a GraphQL query with `limit: 2147483647`) causes the ORM layer to attempt to build/allocate a result set (or issue a `LIMIT` query with a huge row count and buffer the results) sized by attacker-controlled input, with no server-side ceiling.

### Impact Explanation
An authenticated low-privilege node-operator user could submit a single GraphQL query with an extreme `Limit` value, causing the backing store query and subsequent in-memory result marshaling to attempt to allocate proportionally to the row count returned (bounded by actual table size, but for busy nodes with many job runs/transactions this can still be large), potentially exhausting available heap or database resources and degrading/crashing the Operator GUI/API process. This matches the `AV:N/AC:L/PR:L/S:U/C:N/I:N/A:H` profile of the source CVE — availability impact only, no confidentiality/integrity impact, low-privilege authenticated actor, no user interaction.

### Likelihood Explanation
Likelihood is moderate: reaching the resolver requires only an authenticated session (`authenticateUser`), not admin/write privileges, and the request itself is trivial to craft (a GraphQL query specifying a large `Limit`). However, actual impact is bounded by however many rows exist in the underlying tables (`pipeline_runs`, `bridge_types`, relayer nodes) — this is not an arbitrary/unbounded allocation independent of data volume, unlike the Elasticsearch bug which could allocate based on a crafted request shape regardless of index size. This reduces confidence that it reaches the same severity as the CVE.

### Recommendation
Clamp `pageLimit()` (and `ParsePaginatedRequest`'s `size` parameter) to an enforced maximum (e.g., a few thousand) regardless of client input, returning a validation error or silently capping the value when the requested limit exceeds the maximum, consistent with the batch-size limiter pattern already used elsewhere in the codebase (e.g., `RequestValidator.CheckRequestBatchSize` in the Vault capability) [7](#0-6) .

### Proof of Concept
```graphql
query {
  jobRuns(limit: 2147483647, offset: 0) {
    results { id }
    metadata { total }
  }
}
```
Sent by any authenticated session user to the Operator GUI GraphQL endpoint; `pageLimit()` passes `2147483647` unchanged to `JobORM().PipelineRuns`, which is used as the SQL `LIMIT`/row-fetch size with no server-side cap.

**Caveat:** I could not fully verify the underlying ORM implementation of `PipelineRuns`/`BridgeTypes`/`NodeStatuses` (e.g., whether they stream rows or materialize a full slice before returning) within the available index, so the actual allocation behavior and severity depend on that unverified implementation detail.

### Citations

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

**File:** core/web/resolver/query.go (L50-67)
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

**File:** core/web/resolver/query.go (L415-431)
```go
func (r *Resolver) JobRuns(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*JobRunsPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	limit := pageLimit(args.Limit)
	offset := pageOffset(args.Offset)

	runs, count, err := r.App.JobORM().PipelineRuns(ctx, nil, offset, limit)
	if err != nil {
		return nil, err
	}

	return NewJobRunsPayload(runs, safeInt32(count), r.App), nil
```

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

**File:** core/capabilities/vault/validator.go (L254-262)
```go
func (r *RequestValidator) CheckRequestBatchSize(ctx context.Context, batchSize int) error {
	if err := r.MaxRequestBatchSizeLimiter.Check(ctx, batchSize); err != nil {
		if _, ok := errors.AsType[limits.ErrorBoundLimited[int]](err); ok {
			return fmt.Errorf("max batch size exceeded for request: %w", err)
		}
		return errors.New("failed to check batch size")
	}
	return nil
}
```
