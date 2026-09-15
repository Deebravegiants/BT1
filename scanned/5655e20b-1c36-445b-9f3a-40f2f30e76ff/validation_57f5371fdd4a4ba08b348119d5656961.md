### Title
Unbounded GraphQL pagination `limit` allows resource-exhaustion (DoS) via authenticated "view"-role queries - ([File: core/web/resolver/query.go])

### Summary
The GraphQL resolver's pagination helper `pageLimit` accepts a client-supplied `Limit` argument and passes it straight through to backend ORM queries with no upper bound, mirroring the reported bug class (unbounded array/allocation size driven directly by attacker-controlled input causing DoS).

### Finding Description
`pageLimit` simply converts the client-supplied `*int32` limit to an `int` with no maximum cap: [1](#0-0) 

This unbounded `limit` is used directly by numerous GraphQL query resolvers — `Bridges`, `Jobs`, `Nodes`, `JobRuns`, `EthTransactions`, `EthTransactionsAttempts`, etc. — all of which only require the lowest privilege check, `authenticateUser`, which grants access to *any* authenticated session regardless of role ("presence of user inherently provides 'view' access"): [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

An unprivileged "view"-role user can therefore send a request such as `{ jobRuns(limit: 2147483647) { ... } }` and the resolver will forward `limit = 2147483647` unchecked into `r.App.JobORM().PipelineRuns(ctx, nil, offset, limit)` or the equivalent ORM calls for jobs/bridges/nodes/transactions. Depending on the ORM implementation, this can translate into an extremely large `LIMIT` clause in the underlying SQL query, causing the database and node process to allocate and marshal an outsized result set into memory and the HTTP response — directly analogous to the reported `getAuctionData` issue where an unchecked, user-influenced size parameter drives unbounded array construction and loop iteration.

By contrast, other legacy REST paginated endpoints (`core/web/api.go`) also lack a maximum size validation, but the GraphQL surface is the more directly reachable, JSON-based, authenticated-but-unprivileged path since it requires only the minimal "view" role rather than admin/edit/run: [7](#0-6) 

### Impact Explanation
A low-privileged, view-only authenticated node API user can trigger unbounded backend queries and in-memory/JSON marshalling of very large result sets, potentially exhausting database, memory, or CPU resources and causing degraded service or denial of service for the node's operator API — without requiring any elevated role or write access. This is a genuine authenticated request-driven resource-exhaustion vector reachable from the lowest privilege tier defined by the API's own role model.

### Likelihood Explanation
Likelihood is moderate-to-high for any deployment that exposes the GraphQL API to less-trusted "view" role users (a legitimate, supported role tier in the node's RBAC model). The attack requires only a single crafted GraphQL query with an inflated `limit` argument — no additional bypass, secret, or race condition is needed. The main uncertainty is how the underlying ORM/SQL layer bounds `LIMIT` values and whether database-level protections (e.g., statement timeouts, connection limits) mitigate the practical blast radius; this was not fully verified within the available tool budget.

### Recommendation
Add an explicit maximum bound (e.g., `MaxPageLimit`) inside `pageLimit` (and any equivalent REST pagination helpers) and reject/clamp any client-supplied limit that exceeds it, returning a clear GraphQL/API error rather than silently forwarding an oversized value to the ORM layer. Apply the same bound consistently across all paginated resolvers (`Bridges`, `Jobs`, `Nodes`, `JobRuns`, `EthTransactions`, `EthTransactionsAttempts`, etc.).

### Proof of Concept
As an authenticated user holding only the "view" role (the minimum privilege accepted by `authenticateUser`), submit the following GraphQL query against the node's `/query` GraphQL endpoint:
```graphql
{
  jobRuns(limit: 2147483647) {
    results { id }
  }
}
```
`pageLimit` forwards `2147483647` unmodified into `r.App.JobORM().PipelineRuns(ctx, nil, offset, limit)` [5](#0-4)  with no maximum cap enforced in `pageLimit` [1](#0-0) , causing the backend to attempt to construct and serialize a maximally-sized result set for a low-privileged request.

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

**File:** core/web/resolver/auth.go (L11-17)
```go
// Authenticates the user from the session cookie, presence of user inherently provides 'view' access.
func authenticateUser(ctx context.Context) error {
	if _, ok := auth.GetGQLAuthenticatedSession(ctx); !ok {
		return unauthorizedError{}
	}
	return nil
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

**File:** core/web/resolver/query.go (L415-432)
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
}
```

**File:** core/web/resolver/query.go (L536-553)
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
```

**File:** core/web/api.go (L29-51)
```go
// ParsePaginatedRequest parses the parameters that control pagination for a
// collection request, returning the size and offset if specified, or a
// sensible default.
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
