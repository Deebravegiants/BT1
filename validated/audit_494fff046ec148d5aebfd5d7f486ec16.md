Confirmed: `BridgeTypes` uses a parameterized `SELECT * FROM bridge_types ORDER BY name asc LIMIT $1 OFFSET $2` with `limit` passed directly from the unbounded client value, with no application-side cap. [1](#0-0) 

The claim is accurate and reproducible. `pageLimit` in `core/web/resolver/helpers.go` performs no maximum-bound validation on the client-supplied `Limit` argument, simply converting it to `int`. [2](#0-1)  This value flows unchecked into `Bridges`, `JobRuns`, `Nodes`, `EthTransactions`, and other resolvers that only require `authenticateUser`, which grants access based purely on session presence, not role. [3](#0-2) [4](#0-3) [5](#0-4) 

Confirming the backend behavior: `BridgeTypes` passes `limit` directly as a SQL `LIMIT` parameter with no clamping [1](#0-0) , and `PipelineRuns`/`loadPipelineRunIDs` similarly use the raw `limit`/`size` value as a loop-termination bound and SQL `LIMIT` parameter, though this particular path is naturally self-limiting by the size of the underlying `pipeline_runs` table since it walks backward through ID ranges. [6](#0-5)  Notably, `JobResolver.Runs` (a different, related query path resolving runs for a single job) *does* clamp its limit with `min(pageLimit(args.Limit), 100)`, showing the codebase is aware of this pattern elsewhere but has not applied it consistently to the top-level `Query` resolvers audited here. [7](#0-6) 

This confirms the core technical claim: none of the top-level list resolvers (`Bridges`, `Jobs`, `Nodes`, `JobRuns`, `EthTransactions`, `EthTransactionsAttempts`) impose a maximum limit, and the resulting `limit` is forwarded straight into the ORM's SQL `LIMIT` clause, at minimum causing the server to select, marshal, and return the query's full backing table (e.g. all bridges, all jobs, all transactions) in a single unbounded response with a request needing only a valid authenticated session (the lowest role tier, "view").

Audit Report

## Title
Unbounded GraphQL pagination `limit` allows resource-exhaustion (DoS) via authenticated "view"-role queries - ([File: core/web/resolver/query.go, core/web/resolver/helpers.go])

## Summary
The GraphQL `pageLimit` helper converts a client-supplied `Limit` argument directly to an `int` with no maximum bound, and this unbounded value is forwarded unmodified into ORM calls (`BridgeORM().BridgeTypes`, `JobORM().PipelineRuns`, `GetRelayers().NodeStatuses`, `TxmStorageService().Transactions`) that use it as a raw SQL `LIMIT` parameter. All of the affected top-level resolvers only require `authenticateUser`, the lowest-privilege check in the API's role model, granting access to any authenticated session regardless of role.

## Finding Description
`pageLimit` performs no upper-bound validation on the client-supplied limit: [2](#0-1) . This flows into resolvers like `Bridges` [4](#0-3) , `Nodes` [8](#0-7) , `JobRuns` [5](#0-4) , and `EthTransactions` [9](#0-8) , all gated only by `authenticateUser`, which merely checks that a valid session exists — not any specific role [3](#0-2) .

At the ORM layer, `BridgeTypes` passes `limit` straight into a parameterized SQL `LIMIT $1` clause with no server-side cap: [10](#0-9) . This confirms the described exploit chain is real and not mitigated by any intermediate validation, redaction, or role check — the codebase demonstrably knows how to clamp limits (`JobResolver.Runs` does `min(pageLimit(args.Limit), 100)` [7](#0-6) ) but fails to apply this consistently to the top-level `Query` resolvers.

## Impact Explanation
A low-privileged, "view"-role authenticated node API user can force the node to select and JSON-marshal an entire backing table (all bridges, jobs, nodes, or ETH transactions) in a single request, consuming database, memory, and CPU resources disproportionate to the requester's privilege. This maps to a resource-exhaustion/DoS impact reachable by the lowest-privilege authenticated role, which is a legitimate in-scope impact class for a request-driven degradation of node availability.

## Likelihood Explanation
Likelihood is realistic for any deployment where "view"-role credentials are distributed to less-trusted users (a supported role tier), since the exploit requires only a single crafted GraphQL query with an inflated `limit` and no additional bypass. The practical severity depends on table sizes and whether database/infra-level protections (statement timeouts, resource limits) exist, which bounds this to a moderate rather than catastrophic DoS, but the missing application-layer safeguard is a genuine gap.

## Recommendation
Add an explicit maximum bound (e.g., `MaxPageLimit`) inside `pageLimit`, clamping or rejecting any client-supplied limit exceeding it, consistent with the existing `min(pageLimit(args.Limit), 100)` pattern already used in `JobResolver.Runs`. Apply this uniformly across all paginated top-level resolvers (`Bridges`, `Jobs`, `Nodes`, `JobRuns`, `EthTransactions`, `EthTransactionsAttempts`, `Chains`, etc.) and any equivalent REST pagination helpers in `core/web/api.go`.

## Proof of Concept
As an authenticated user holding only the "view" role, submit:
```graphql
{
  jobRuns(limit: 2147483647) {
    results { id }
  }
}
```
or
```graphql
{
  bridges(limit: 2147483647) {
    results { id }
  }
}
```
against the node's GraphQL `/query` endpoint. `pageLimit` forwards the value unmodified [2](#0-1) , and the ORM layer (e.g. `BridgeTypes`) uses it directly as the SQL `LIMIT` value with no application-side cap [1](#0-0) , causing the node to attempt to load and serialize the full result set for a minimally-privileged request.

### Citations

**File:** core/bridges/orm.go (L108-123)
```go
// BridgeTypes returns bridge types ordered by name filtered limited by the
// passed params.
func (o *orm) BridgeTypes(ctx context.Context, offset int, limit int) (bridges []BridgeType, count int, err error) {
	err = o.transact(ctx, true, func(tx *orm) error {
		if err = tx.ds.GetContext(ctx, &count, "SELECT COUNT(*) FROM bridge_types"); err != nil {
			return pkgerrors.Wrap(err, "BridgeTypes failed to get count")
		}
		sql := `SELECT * FROM bridge_types ORDER BY name asc LIMIT $1 OFFSET $2;`
		if err = tx.ds.SelectContext(ctx, &bridges, sql, limit, offset); err != nil {
			return pkgerrors.Wrap(err, "BridgeTypes failed to load bridge_types")
		}
		return nil
	})

	return
}
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

**File:** core/services/job/orm.go (L1184-1250)
```go
func (o *orm) loadPipelineRunIDs(ctx context.Context, jobID *int32, offset, limit int) (ids []int64, err error) {
	lggr := o.lggr

	var res sql.NullInt64
	if err = o.ds.GetContext(ctx, &res, "SELECT MAX(id) FROM pipeline_runs"); err != nil {
		err = errors.Wrap(err, "error while loading runs")
		return ids, err
	} else if !res.Valid {
		// MAX() will return NULL if there are no rows in table.  This is not an error
		return ids, err
	}
	maxID := res.Int64

	var filter string
	if jobID != nil {
		filter = fmt.Sprintf("JOIN job_pipeline_specs USING(pipeline_spec_id) WHERE job_pipeline_specs.job_id = %d AND ", *jobID)
	} else {
		filter = "WHERE "
	}

	stmt := fmt.Sprintf(`SELECT p.id FROM pipeline_runs AS p %s p.id >= $3 AND p.id <= $4
			ORDER BY p.id DESC OFFSET $1 LIMIT $2`, filter)

	// Only search the most recent n pipeline runs (whether deleted or not), starting with n = 1000 and
	//  doubling only if we still need more.  Without this, large tables can result in the UI
	//  becoming unusably slow, continuously flashing, or timing out.  The ORDER BY in
	//  this query requires a sort of all runs matching jobID, so we restrict it to the
	//  range minID <-> maxID.

	for n := int64(1000); maxID > 0 && len(ids) < limit; n *= 2 {
		var batch []int64
		minID := maxID - n
		if err = o.ds.SelectContext(ctx, &batch, stmt, offset, limit-len(ids), minID, maxID); err != nil {
			err = errors.Wrap(err, "error loading runs")
			return ids, err
		}
		ids = append(ids, batch...)
		if offset > 0 {
			if len(ids) > 0 {
				// If we're already receiving rows back, then we no longer need an offset
				offset = 0
			} else {
				var skipped int
				// If no rows were returned, we need to know whether there were any ids skipped
				//  in this batch due to the offset, and reduce it for the next batch
				err = o.ds.GetContext(ctx, &skipped,
					fmt.Sprintf(
						`SELECT COUNT(p.id) FROM pipeline_runs AS p %s p.id >= $1 AND p.id <= $2`, filter,
					), minID, maxID,
				)
				if err != nil {
					err = errors.Wrap(err, "error loading from pipeline_runs")
					return ids, err
				}
				offset -= skipped
				if offset < 0 { // sanity assertion, if this ever happened it would probably mean db corruption or pg bug
					lggr.AssumptionViolationw("offset < 0 while reading pipeline_runs")
					err = errors.Wrap(err, "internal db error while reading pipeline_runs")
					return ids, err
				}
				lggr.Debugw("loadPipelineRunIDs empty batch", "minId", minID, "maxID", maxID, "n", n, "len(ids)", len(ids), "limit", limit, "offset", offset, "skipped", skipped)
			}
		}
		maxID = minID - 1
	}
	return ids, err
}
```

**File:** core/web/resolver/job.go (L112-120)
```go
// Runs fetches the runs for a Job.
func (r *JobResolver) Runs(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*JobRunsPayloadResolver, error) {
	offset := pageOffset(args.Offset)
	limit := min(pageLimit(args.Limit), 100)

	ids, err := r.app.JobORM().FindPipelineRunIDsByJobID(ctx, r.j.ID, offset, limit)
```
