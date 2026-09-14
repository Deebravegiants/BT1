## Title
GraphQL `/query` endpoint permits unauthenticated introspection and unbounded alias/field-duplication DoS - (File: `core/web/router.go`)

### Summary
The node's GraphQL endpoint (`POST /query`) is reachable by unauthenticated clients because the session-checking middleware never aborts the request on failed authentication, and the schema is only hardened against query *depth*, not against alias overloading, field duplication, or introspection itself. This reproduces the exact bug classes described in the external report (Alias Overloading, Field Duplication, Introspection Query by unauthenticated users) against a concrete, unprivileged-reachable path.

### Finding Description
`NewRouter` mounts the GraphQL endpoint with `auth.AuthenticateGQL` as the *only* authentication step before the handler runs: [1](#0-0) 

`AuthenticateGQL` is designed to be non-blocking: if there is no valid session cookie, it simply returns without calling `c.Abort()`, so gin continues to the next middleware/handler instead of rejecting the request: [2](#0-1) 

The GraphQL schema is built with only a depth limit, gated behind the `InfiniteDepthQueries` insecure flag (default off, so `MaxDepth(10)` normally applies) — there is no alias-count limit, no field-duplication check, and introspection is never disabled: [3](#0-2) 

Per-resolver authorization (`authenticateUser`, `authenticateUserCanRun`, `authenticateUserCanEdit`, `authenticateUserIsAdmin`) is only invoked from inside the custom `Resolver` methods for `Query`/`Mutation` fields: [4](#0-3) 

Introspection fields (`__schema`, `__type`) are resolved internally by the `graph-gophers/graphql-go` library itself and never pass through these custom resolver functions, so they are not subject to `authenticateUser`. Because `AuthenticateGQL` never blocks unauthenticated requests from reaching `graphqlHandler`, an unauthenticated, unprivileged client can:
- Run the full introspection query and dump the entire node GraphQL schema.
- Send queries using 100+ aliases or hundreds of duplicated fields (bounded only by `MaxDepth(10)` and the generic HTTP body size limiter, `limits.RequestSizeLimiter`), causing the server to redundantly execute/resolve the same operation many times within the allowed depth.

### Impact Explanation
An unauthenticated actor can cause amplified resource consumption (CPU/DB load) on the operator node purely from the internet-facing HTTP surface, and can enumerate the entire private GraphQL schema (query/mutation names, types, field names) without any credentials — aiding further attacks. This matches Impact rated in the source report (application-level DoS + information disclosure), and here it is reachable without any authentication at all, which is a stronger condition than the original report against Fuelet.

### Likelihood Explanation
Likelihood is moderate: the `/query` route is exposed on the node's web server, protected only by a generic HTTP rate limiter (`rateLimiter` using `rl.AuthenticatedPeriod()/rl.Authenticated()` request counts) and body-size limiting, neither of which caps alias count, duplicate field count, or introspection use. No credentials, session, or special network position are required — a single unauthenticated HTTP POST is sufficient.

### Recommendation
- Make `AuthenticateGQL` (or a wrapping middleware) reject/abort unauthenticated requests to `/query` outright, consistent with how `auth.Authenticate` aborts on failure for the REST v2 routes, rather than silently proceeding without a session.
- Disable GraphQL introspection in production builds (or gate it behind an explicit insecure/dev flag, similar to `InfiniteDepthQueries`).
- Add alias-count and duplicate-field validation rules (e.g., via a custom `graphql.RuleFunc`/validation similar to `graphql-no-alias`) when constructing the schema in `graphqlHandler`, in addition to the existing `MaxDepth(10)`.

### Proof of Concept
1. Send `POST /query` with no session cookie and body:
```graphql
{ __schema { types { name fields { name } } } }
```
This succeeds because `AuthenticateGQL` does not abort unauthenticated requests before `graphqlHandler` executes the query, and `__schema` resolution bypasses `authenticateUser`.
2. Send `POST /query` with no session cookie and a query using 100+ aliases against a permitted-depth field, e.g.:
```graphql
{ a0: bridges { results { id } } a1: bridges { results { id } } ... a100: bridges { results { id } } }
```
Each alias is independently executed by the library, multiplying backend work per request, without triggering any alias/field-duplication limit in `core/web/router.go`'s `graphqlHandler`.

### Citations

**File:** core/web/router.go (L95-99)
```go
	api.POST("/query",
		auth.AuthenticateGQL(app.AuthenticationProvider(), app.GetLogger().Named("GQLHandler")),
		loader.Middleware(app),
		graphqlHandler(app),
	)
```

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
