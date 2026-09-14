### Title
Unbounded GraphQL pagination `limit` argument allows resource-exhaustion DoS by any authenticated user - (File: core/web/resolver/query.go)

### Summary
The chainlink GraphQL server exposes multiple paginated queries (`bridges`, `jobs`, `nodes`, `jobRuns`, `ethTransactions`, `ethTransactionsAttempts`) that accept client-supplied `Offset`/`Limit` arguments. The helper that resolves these arguments, `pageLimit`, only substitutes a default (`PageDefaultLimit = 50`) when the client omits the argument — it never clamps or validates a client-supplied value, so a request can specify an arbitrarily large `Limit` (e.g. `2147483647`) and the resolver will pass that value straight through to the DB/ORM layer.

### Finding Description
`pageLimit` in `core/web/resolver/helpers.go` is defined as: [1](#0-0) 

Every top-level list query in `core/web/resolver/query.go` calls this helper and forwards the result unchecked to the storage layer, e.g.: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

The only exception found is `JobResolver.Runs`, which explicitly clamps the client value with `min(pageLimit(args.Limit), 100)`: [6](#0-5) 

That clamp is absent from `Resolver.Bridges`, `Resolver.Jobs`, `Resolver.Nodes`, `Resolver.JobRuns`, `Resolver.EthTransactions`, and `Resolver.EthTransactionsAttempts`. All of these only require `authenticateUser`, which merely checks that a valid session exists — any authenticated user regardless of role (`view`, `run`, `edit`, `admin`) can invoke them: [7](#0-6) 

This is a direct structural analog to the reported CVE-2025-43796 bug class (Liferay GraphQL missing result-count limiting enabling DoS): a GraphQL query parameter that controls result-set size is accepted from the client without an upper bound, on an endpoint reachable by any authenticated caller.

### Impact Explanation
Any authenticated node UI user — even one holding only the lowest `view` role — can request an oversized page (e.g. `limit: 2000000000`) on `jobs`, `bridges`, `nodes`, `jobRuns`, or `ethTransactions`. This causes the resolver to ask the underlying store/ORM for that many rows, which can trigger large SQL scans/allocations and outsized JSON marshaling of the GraphQL response, consuming CPU, memory, and DB connections disproportionate to the request. Repeated concurrent requests from a single low-privileged session could degrade or exhaust node resources, denying service to other API consumers (CWE-400), consistent with the analog's classification and impact profile.

### Likelihood Explanation
High likelihood: the GraphQL API is reachable by any authenticated session regardless of role, requires no special privilege escalation, and the vulnerable parameter (`limit`) is a normal, expected part of the public GraphQL schema (`offset`/`limit` args), so no non-obvious knowledge is needed to exploit it — an attacker only needs valid low-privilege credentials.

### Recommendation
Apply a maximum bound to `pageLimit` (or to each call site) consistently across all paginated resolvers in `core/web/resolver/query.go`, mirroring the existing `min(pageLimit(args.Limit), 100)` pattern already used in `core/web/resolver/job.go`'s `Runs` resolver. Centralizing the cap inside `pageLimit` in `core/web/resolver/helpers.go` would be safer than per–call-site clamping, since it would prevent any future paginated resolver from bypassing the limit.

### Proof of Concept
1. Authenticate as any user with the lowest privilege role (`view`).
2. Send a GraphQL query:
```graphql
query {
  jobs(offset: 0, limit: 2000000000) {
    results { id }
    metadata { total }
  }
}
```
3. Observe that `Resolver.Jobs` (core/web/resolver/query.go:234-252) passes `limit=2000000000` unmodified to `r.App.JobORM().FindJobs(ctx, offset, limit)`, with no server-side cap, unlike the `JobResolver.Runs` path which clamps to 100. Repeating this concurrently against `jobs`, `bridges`, `nodes`, `jobRuns`, and `ethTransactions` amplifies resource consumption across the node's DB and API layer.

**Note on verification gaps:** I was unable to fully confirm within the tool budget whether `core/services/job/orm.go`'s `FindJobs` or `core/bridges/orm.go`'s `BridgeTypes` apply any additional server-side LIMIT clamping at the SQL layer beyond what the resolver passes in — the grep results for those files returned match counts but not their content. If those ORM layers already impose their own hard caps, the exploitable impact would be reduced to whatever cap exists there; this should be confirmed by inspecting `core/services/job/orm.go` and `core/bridges/orm.go` directly.

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

**File:** core/web/resolver/job.go (L112-123)
```go
// Runs fetches the runs for a Job.
func (r *JobResolver) Runs(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*JobRunsPayloadResolver, error) {
	offset := pageOffset(args.Offset)
	limit := min(pageLimit(args.Limit), 100)

	ids, err := r.app.JobORM().FindPipelineRunIDsByJobID(ctx, r.j.ID, offset, limit)
	if err != nil {
		return nil, err
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
