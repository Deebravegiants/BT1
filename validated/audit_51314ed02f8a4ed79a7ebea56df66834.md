### Title
Unauthenticated Clients Can Execute Arbitrary GraphQL Queries on the Node's `/query` Endpoint, Enabling Resource-Exhaustion Denial-of-Service - ([File: core/web/auth/gql.go])

### Summary
The chainlink node exposes a GraphQL endpoint at `/query` that is intended to require an authenticated session, but the `AuthenticateGQL` middleware silently no-ops when no valid session is present instead of rejecting the request. Combined with the fact that query-depth limiting is the *only* resource control applied to the GraphQL handler (no complexity/breadth limiting, no response-size cap, and rate limiting is applied uniformly rather than gating access), an unauthenticated or low-privileged network client can reach the full GraphQL execution engine — including introspection — and force the node to parse, validate, and execute expensive queries. This mirrors the reported bug class (CWE-400/CWE-770: unrestricted GraphQL query execution with no resource controls), but on this codebase the exposure is worse because the endpoint does not even require authentication to reach the expensive execution path.

### Finding Description
The route is registered without a hard authentication gate: [1](#0-0) 

`AuthenticateGQL` is supposed to enforce the session, but when the session cookie is absent or invalid it simply `return`s without aborting the Gin context — allowing the request chain (`loader.Middleware` → `graphqlHandler`) to continue processing the query as an unauthenticated request: [2](#0-1) 

The GraphQL handler itself only guards against pure query *depth* (and only in production builds, via `graphql.MaxDepth(10)`); there is no complexity/breadth analysis, no response-size cap, and introspection is not disabled: [3](#0-2) 

`InfiniteDepthQueries()` is gated by `build.IsDev()`, so `MaxDepth(10)` is always applied in production — but depth-10 introspection of the full schema (which has dozens of query root fields, dozens of mutation fields, and many nested spec/key/job types) is still enough to enumerate significant portions of the schema and produce a large response: [4](#0-3) [5](#0-4) 

The `/query` route sits in the same Gin group as all other authenticated API routes and is rate-limited using the *authenticated* tier (`rl.AuthenticatedPeriod()`, `rl.Authenticated()`), not a separate, stricter unauthenticated tier: [6](#0-5) 

Because `AuthenticateGQL` never blocks the request, an anonymous caller is subjected to this same (generous) authenticated-tier quota while never having to authenticate — i.e., the intended authentication gate for this endpoint is bypassed, and per-field authorization checks (seen in resolvers like `mutation.go`/`auth.go`) only apply to specific mutation resolvers, not to the parse/validate/execute pipeline itself, which is where the resource cost of the reported bug class is incurred.

### Impact Explanation
An unauthenticated network client that can reach the node's web server can repeatedly submit GraphQL queries (including introspection or breadth-heavy queries against fields like `jobs`, `ethTransactions`, `bridges`, etc., up to depth 10) without ever presenting valid credentials. Since there is no per-field complexity budget or response-size cap, and the applicable rate limit is the more permissive "authenticated" quota rather than a hard authentication requirement, an attacker can drive sustained CPU/memory/bandwidth consumption on the node's web server process, degrading or denying service to legitimate operators of the node — matching the Availability-High impact profile of the original advisory, but reachable without any privileges at all on this codebase.

### Likelihood Explanation
High. The `/query` endpoint is exposed on the node's standard HTTP web server (no unusual configuration required), and the authentication bypass is a straightforward code path: simply omit or use an invalid session cookie. No exploitation complexity beyond crafting a GraphQL query (well within depth 10) and issuing repeated/parallel HTTP POSTs is required.

### Recommendation
1. Make `AuthenticateGQL` abort the request (e.g., `c.AbortWithStatus(http.StatusUnauthorized)`) when no valid session is found, rather than silently continuing, so unauthenticated requests never reach the GraphQL execution engine.
2. Add query complexity/cost analysis (not just depth) to `graphqlHandler` in `core/web/router.go`, and consider capping response size.
3. Apply a distinct, stricter unauthenticated rate-limit tier to `/query` if any pre-auth access is intentionally allowed (e.g., for a login-adjacent flow), otherwise remove it from the shared "authenticated" rate limiter group.
4. Ensure introspection is disabled or heavily throttled outside of development builds.

### Proof of Concept
1. Send `POST /query` with no session cookie and a body such as:
```graphql
{
  __schema {
    types {
      name
      fields {
        name
        type { name kind ofType { name kind ofType { name kind } } }
      }
    }
  }
}
```
2. Observe the query executes and returns full schema data despite no `Authorization`/session cookie being sent, confirming `AuthenticateGQL` (`core/web/auth/gql.go`) did not block the request.
3. Script repeated/parallel submission of this (or a wide, aliased, depth-10 query against `jobs`/`ethTransactions`) from a single unauthenticated client to observe CPU/memory growth and degraded response times on the node's web server, consistent with the rate limiter permitting the "authenticated" quota tier for these unauthenticated requests.

### Citations

**File:** core/web/router.go (L76-99)
```go
	engine.Use(helmet.Default())
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

**File:** core/services/chainlink/config_insecure.go (L28-31)
```go
func (i *insecureConfig) InfiniteDepthQueries() bool {
	return build.IsDev() && i.c.InfiniteDepthQueries != nil &&
		*i.c.InfiniteDepthQueries
}
```

**File:** core/web/schema/schema.graphql (L10-82)
```text
type Query {
    bridge(id: ID!): BridgePayload!
    bridges(offset: Int, limit: Int): BridgesPayload!
    chain(id: ID!, network: String): ChainPayload!
    chains(offset: Int, limit: Int): ChainsPayload!
    configv2: ConfigV2Payload!
    csaKeys: CSAKeysPayload!
    ethKeys: EthKeysPayload!
    ethTransaction(hash: ID!): EthTransactionPayload!
    ethTransactions(offset: Int, limit: Int): EthTransactionsPayload!
    ethTransactionsAttempts(offset: Int, limit: Int): EthTransactionAttemptsPayload!
    features: FeaturesPayload!
    feedsManager(id: ID!): FeedsManagerPayload!
    feedsManagers: FeedsManagersPayload!
    globalLogLevel: GlobalLogLevelPayload!
    job(id: ID!): JobPayload!
    jobs(offset: Int, limit: Int): JobsPayload!
    jobProposal(id: ID!): JobProposalPayload!
    jobRun(id: ID!): JobRunPayload!
    jobRuns(offset: Int, limit: Int): JobRunsPayload!
    node(id: ID!): NodePayload!
    nodes(offset: Int, limit: Int): NodesPayload!
    ocrKeyBundles: OCRKeyBundlesPayload!
    ocr2KeyBundles: OCR2KeyBundlesPayload!
    p2pKeys: P2PKeysPayload!
    solanaKeys: SolanaKeysPayload!
    aptosKeys: AptosKeysPayload!
    suiKeys: SuiKeysPayload!
    cosmosKeys: CosmosKeysPayload!
    starknetKeys: StarkNetKeysPayload!
    tronKeys: TronKeysPayload!
    tonKeys: TONKeysPayload!
    stellarKeys: StellarKeysPayload!
    sqlLogging: GetSQLLoggingPayload!
    vrfKey(id: ID!): VRFKeyPayload!
    vrfKeys: VRFKeysPayload!
}

type Mutation {
    approveJobProposalSpec(id: ID!, force: Boolean): ApproveJobProposalSpecPayload!
    cancelJobProposalSpec(id: ID!): CancelJobProposalSpecPayload!
    createAPIToken(input: CreateAPITokenInput!): CreateAPITokenPayload!
    createBridge(input: CreateBridgeInput!): CreateBridgePayload!
    createCSAKey: CreateCSAKeyPayload!
    createFeedsManager(input: CreateFeedsManagerInput!): CreateFeedsManagerPayload!
    createFeedsManagerChainConfig(input: CreateFeedsManagerChainConfigInput!): CreateFeedsManagerChainConfigPayload!
    createJob(input: CreateJobInput!): CreateJobPayload!
    createOCRKeyBundle: CreateOCRKeyBundlePayload!
    createOCR2KeyBundle(chainType: OCR2ChainType!): CreateOCR2KeyBundlePayload!
    createP2PKey: CreateP2PKeyPayload!
    deleteAPIToken(input: DeleteAPITokenInput!): DeleteAPITokenPayload!
    deleteBridge(id: ID!): DeleteBridgePayload!
    deleteCSAKey(id: ID!): DeleteCSAKeyPayload!
    deleteFeedsManagerChainConfig(id: ID!): DeleteFeedsManagerChainConfigPayload!
    deleteJob(id: ID!): DeleteJobPayload!
    deleteOCRKeyBundle(id: ID!): DeleteOCRKeyBundlePayload!
    deleteOCR2KeyBundle(id: ID!): DeleteOCR2KeyBundlePayload!
    deleteP2PKey(id: ID!): DeleteP2PKeyPayload!
    createVRFKey: CreateVRFKeyPayload!
    deleteVRFKey(id: ID!): DeleteVRFKeyPayload!
    dismissJobError(id: ID!): DismissJobErrorPayload!
    rejectJobProposalSpec(id: ID!): RejectJobProposalSpecPayload!
    runJob(id: ID!): RunJobPayload!
    setGlobalLogLevel(level: LogLevel!): SetGlobalLogLevelPayload!
    setSQLLogging(input: SetSQLLoggingInput!): SetSQLLoggingPayload!
    updateBridge(id: ID!, input: UpdateBridgeInput!): UpdateBridgePayload!
    updateFeedsManager(id: ID!, input: UpdateFeedsManagerInput!): UpdateFeedsManagerPayload!
    enableFeedsManager(id: ID!): EnableFeedsManagerPayload!
    disableFeedsManager(id: ID!): DisableFeedsManagerPayload!
    updateFeedsManagerChainConfig(id: ID!, input: UpdateFeedsManagerChainConfigInput!): UpdateFeedsManagerChainConfigPayload!
    updateJobProposalSpecDefinition(id: ID!, input: UpdateJobProposalSpecDefinitionInput!): UpdateJobProposalSpecDefinitionPayload!
    updateUserPassword(input: UpdatePasswordInput!): UpdatePasswordPayload!
}
```
