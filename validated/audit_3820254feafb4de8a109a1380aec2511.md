### Title
GraphQL Field/Alias Duplication Denial of Service via `/query` Endpoint - ([File: core/web/router.go])

### Summary
The Chainlink node's GraphQL endpoint at `POST /query` only applies a **query-depth** limit (`graphql.MaxDepth(10)`) when `Insecure().InfiniteDepthQueries()` is disabled, but it applies no limit on **query breadth** — i.e., the number of times a field can be repeated or aliased at the same nesting level. This mirrors the Directus GHSA-7hmh-pfrp-vcx4 field-duplication DoS: an attacker can request the same shallow field thousands of times without ever increasing nesting depth, evading `MaxDepth` entirely while forcing the server to construct and resolve a massive response tree.

### Finding Description
`NewRouter` wires up the GraphQL handler like this: [1](#0-0) 

Only `graphql.MaxDepth(10)` is conditionally added as a schema option — there is no complexity/cost limiting, no maximum field count, and no alias-count limiting: [2](#0-1) 

`MaxDepth` (from `graph-gophers/graphql-go`) only bounds how deeply queries can nest (parent→child chains). It does **not** bound how many sibling fields or aliases can be requested at a single level. A query such as:

```graphql
query {
  jobs { results { id } results { id } results { id } ... x N }
}
```

remains at constant depth while the resolver, `graph-gophers/graphql-go` field execution, and eventual JSON marshaling all scale linearly (or worse, given nested payload objects like `results`/`metadata`) with the number of duplicated field selections — exactly the bug class described in the Directus advisory.

Access to this endpoint requires only a valid session cookie, not a privileged role — `AuthenticateGQL` simply looks up any authenticated session and attaches it to the context: [3](#0-2) 

Individual resolvers (e.g., `Bridges`, `JobRuns`, `Nodes`, `EthTransactions`) call `authenticateUser(ctx)`, which only checks that a session/user is present — it is not scoped to admin-only roles, so any low-privilege authenticated user (e.g., a "view"-role Operator UI user) can reach these paginated/nested queries: [4](#0-3) [5](#0-4) 

The gateway's HTTP layer (`core/services/gateway/network/httpserver.go`) does enforce a request-size limiter, but that only bounds raw payload bytes, not the number of duplicated fields the GraphQL parser must resolve within that byte budget — a compact query text can still expand into an enormous execution/response graph (analogous to the "small payload, huge blast radius" nature of the original PoC).

### Impact Explanation
A single authenticated (even low-privilege) user can send a GraphQL query that duplicates a field or list-returning selection (e.g., `results`, `metadata`, nested payload types) many times at one nesting level. Since `MaxDepth` does not restrict breadth, the query is accepted, and the node performs redundant resolver execution and JSON serialization for each duplicate, consuming CPU/memory and potentially rendering the node's web/API surface (including the Operator UI and node-management API) unresponsive — a denial of service against node availability, matching CWE-400 and the CVSS `A:H` impact of the source advisory.

### Likelihood Explanation
Likelihood is high for any actor who already holds valid, even minimally privileged, node credentials (a "view"-only Operator UI account), since:
- The endpoint accepts arbitrary GraphQL text within the size limit.
- No complexity/breadth validation exists beyond `MaxDepth`.
- No per-request cost/timeout specific to GraphQL execution is enforced beyond the generic HTTP request timeout/rate limiter, which does not account for query cost.

This requires authentication, so it is not exploitable pre-auth, but it is a straightforward availability bypass for any authenticated low-privilege session.

### Recommendation
Add a GraphQL query-complexity/cost limiter (e.g., limiting total selection count, alias count, or computed cost per query) alongside the existing `graphql.MaxDepth` schema option in `core/web/router.go`'s `graphqlHandler`. Consider integrating a cost-analysis library or a hard cap on total field selections per query, and apply a strict execution timeout scoped to GraphQL resolution independent of the general HTTP timeout.

### Proof of Concept
Using a valid authenticated session cookie against `POST /query`:
```json
{
  "query": "query { jobRuns { results { id } metadata { total } } jobRuns2: jobRuns { results { id } metadata { total } } jobRuns3: jobRuns { results { id } metadata { total } } /* ... repeated thousands of times with aliases jobRunsN ... */ }"
}
```
Because depth stays at a small constant (well under 10) while breadth (number of aliased top-level/nested selections) grows unbounded, `graphql.MaxDepth(10)` does not reject the query, and the server must resolve and serialize each duplicated branch, analogous to the Directus `max { id id id ... }` repetition PoC.

### Citations

**File:** core/web/router.go (L109-134)
```go
// Defining the Graphql handler
func graphqlHandler(app chainlink.Application) gin.HandlerFunc {
	rootSchema := schema.MustGetRootSchema()

	// Disable introspection and set a max query depth in production.
	var schemaOpts []graphql.SchemaOpt

	if !app.GetConfig().Insecure().InfiniteDepthQueries() {
		schemaOpts = append(schemaOpts,
			graphql.MaxDepth(10),
		)
	}

	schema := graphql.MustParseSchema(rootSchema,
		&resolver.Resolver{
			App: app,
		},
		schemaOpts...,
	)

	h := relay.Handler{Schema: schema}

	return func(c *gin.Context) {
		h.ServeHTTP(c.Writer, c.Request)
	}
}
```

**File:** core/web/auth/gql.go (L25-48)
```go
func AuthenticateGQL(authenticator Authenticator, lggr logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := c.Request.Context()
		session := sessions.Default(c)
		sessionID, ok := session.Get(SessionIDKey).(string)
		if !ok {
			return
		}

		user, err := authenticator.AuthorizedUserWithSession(ctx, sessionID)
		if err != nil {
			if errors.Is(err, clsessions.ErrUserSessionExpired) {
				lggr.Warnw("Failed to authenticate session", "err", err)
			} else {
				lggr.Errorw("Failed call to AuthorizedUserWithSession, unable to get user", "err", err)
			}
			return
		}

		ctx = WithGQLAuthenticatedSession(c.Request.Context(), user, sessionID)

		c.Request = c.Request.WithContext(ctx)
	}
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
