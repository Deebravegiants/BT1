## Analog Finding

### Title
GraphQL API resource exhaustion via unbounded aliased/batched queries and mutations - (File: core/web/router.go)

### Summary
The Chainlink node's GraphQL endpoint enforces only a maximum query *depth* of 10 via `graphql.MaxDepth(10)`, but applies no limit on query *breadth* — the number of aliased root-level fields or chained mutations a client can pack into a single POST to `/query`. This mirrors the Saleor CVE-2026-35401 bug class: an actor can use GraphQL aliases to request or mutate hundreds/thousands of fields in one call, exhausting CPU/DB/goroutine resources, even though depth-based guards are in place.

### Finding Description
The GraphQL handler is constructed in `graphqlHandler` in [1](#0-0) . The only complexity control applied is:

```go
if !app.GetConfig().Insecure().InfiniteDepthQueries() {
    schemaOpts = append(schemaOpts, graphql.MaxDepth(10))
}
``` [2](#0-1) 

There is no `MaxParallelism` limiter, no query-cost/complexity analysis, and no cap on the number of top-level (or aliased) query/mutation selections a single document may contain. `graphql.MaxDepth` only bounds nesting depth, not the count of sibling/aliased fields, so a request such as:

```graphql
query {
  a0: bridges(limit: 50) { results { id name url } }
  a1: bridges(limit: 50) { results { id name url } }
  ... (repeated thousands of times)
}
```

or a single mutation document invoking dozens of `runJob`/`createJob` aliases, passes schema validation untouched because depth stays at 1–2.

The route itself is reachable at `/query`, protected only by a coarse per-period request-count rate limiter (`rl.AuthenticatedPeriod()` / `rl.Authenticated()`), not a per-query cost limiter [3](#0-2) . `AuthenticateGQL` middleware does not reject unauthenticated requests outright — it only conditionally attaches a session to context, explicitly delegating the authorization decision to each resolver: "It is the responsibility of each resolver to validate whether it requires an authenticated user" [4](#0-3) . This means the GraphQL library still parses and begins resolving every aliased field in the document (invoking the relay handler's execution engine) before any individual resolver's `authenticateUser`/role check runs, so the parsing/resolution cost is paid regardless of whether each field ultimately errors out with `unauthorizedError` [5](#0-4) .

For authenticated low-privilege ("view" role) users, whose queries do pass the auth check, each aliased read (e.g. `bridges`, `jobs`, `ethTransactions`, `jobRuns`) triggers a full ORM round trip, so a single request with many aliases multiplies database load linearly with attacker-controlled alias count.

### Impact Explanation
An actor able to reach `/query` (an authenticated low-privilege "view" role session, given per-resolver-only authorization, or effectively any request that reaches the relay handler before resolver-level authorization is enforced) can submit one HTTP request containing an arbitrarily large number of aliased queries or mutations. This multiplies backend work (DB queries, goroutines, JSON serialization) per request, enabling denial-of-service of the node's operator API with a small number of requests — directly matching the CVSS 3.1 vector of the source CVE (`AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`): no confidentiality/integrity impact, but severe availability impact.

### Likelihood Explanation
Likelihood is high for any party with a valid session (even the lowest "view" role, which is intended only for read-only dashboards) since no additional privilege is required to construct an oversized aliased document, and the existing depth/rate-limit controls do not address breadth. The GraphQL endpoint accepts POST bodies up to `HTTPMaxSize()` [6](#0-5) , which is large enough to contain many thousands of short aliased selections.

### Recommendation
Add a query-complexity/cost limit (e.g., graphql-go's `MaxParallelism`/custom complexity middleware, or a custom validator that counts top-level selections and aliases before execution) alongside the existing `MaxDepth(10)`. Reject requests exceeding a configurable maximum node/field count per operation, and consider moving authorization checks (`authenticateUser`) ahead of full query parsing/execution where feasible, e.g. via a pre-execution complexity-estimation pass in `graphqlHandler` in `core/web/router.go`.

### Proof of Concept
1. Authenticate as a "view"-role user (lowest privilege tier) to obtain a session cookie.
2. POST to `/query` a single GraphQL document with a large number of aliases, e.g. programmatically generate:
```graphql
query Flood {
  a0: bridges(limit: 50) { results { id name url } }
  a1: bridges(limit: 50) { results { id name url } }
  ...
  a4999: bridges(limit: 50) { results { id name url } }
}
```
3. Observe that `graphql.MaxDepth(10)` does not reject the document (depth is 2), the request passes the per-period rate limiter as a single call, and the node performs ~5000 DB round trips and resolver evaluations for one HTTP request, consuming disproportionate CPU/DB resources relative to request count — demonstrating the resource-exhaustion class described in CVE-2026-35401.

### Citations

**File:** core/web/router.go (L64-72)
```go
	engine.Use(
		otelgin.Middleware("chainlink-web-routes",
			otelgin.WithTracerProvider(otel.GetTracerProvider())),
		limits.RequestSizeLimiter(config.WebServer().HTTPMaxSize()),
		loggerFunc(app.GetLogger()),
		gin.Recovery(),
		cors,
		secureMiddleware(tls.ForceRedirect(), tls.Host(), config.Insecure().DevWebServer()),
	)
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

**File:** core/web/router.go (L110-134)
```go
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

**File:** core/web/auth/gql.go (L20-47)
```go
// AuthenticateGQL middleware checks the session cookie for a user and sets it
// on the request context if it exists. It is the responsibility of each resolver
// to validate whether it requires an authenticated user.
//
// We currently only support GQL authentication by session cookie.
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
