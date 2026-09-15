### Title
Chainlink node GraphQL endpoint allows unauthenticated schema introspection - (File: `core/web/router.go`)

### Summary
The Chainlink node's GraphQL API endpoint (`POST /query`) is reachable without authentication and does not actually disable GraphQL introspection despite a comment claiming otherwise, allowing any unauthenticated network client to run `__schema`/`__type` introspection queries and enumerate the full node GraphQL schema (all queries, mutations, types, and field names).

### Finding Description
The `/query` route is registered with the `AuthenticateGQL` middleware followed directly by `graphqlHandler`: [1](#0-0) 

`AuthenticateGQL` only *optionally* attaches an authenticated session to the request context if a valid session cookie is present; if there is no session or it is invalid, it simply returns without aborting the request, letting it continue to the GraphQL handler unauthenticated: [2](#0-1) 

The GraphQL handler itself carries a comment stating introspection should be disabled in production, but the code that follows only conditionally sets `graphql.MaxDepth(10)` — there is no `graphql.DisableIntrospection`-equivalent option or resolver-level gate applied to the schema: [3](#0-2) 

Because GraphQL introspection (`__schema`, `__type` meta-fields) is resolved internally by the `graph-gophers/graphql-go` library against the parsed schema AST — not through the `resolver.Resolver` methods — any per-field authorization checks implemented in individual resolvers (e.g., checks against `auth.GetGQLAuthenticatedSession`) are never invoked for introspection queries. An unauthenticated POST to `/query` with a standard introspection query will therefore return the full schema, including all `Query`/`Mutation` fields such as `createAPIToken`, `deleteVRFKey`, `ethKeys`, `csaKeys`, `vrfKeys`, etc., as defined in the schema: [4](#0-3) [5](#0-4) 

This is a direct analog to the reported bug class (GHSA-p76j-h4m8-hx5c / CVE-2023-5192): GraphQL introspection is left enabled and reachable by unauthenticated/unprivileged clients, exposing the complete API schema and sensitive operation names (key management, secrets, job control) that would otherwise inform an attacker's targeting of privileged mutations/queries.

### Impact Explanation
Exposing the full schema to unauthenticated actors is a CWE-200/CWE-1049 information-disclosure issue: it reveals every available query/mutation name, argument, and return type (including sensitive operations like `createAPIToken`, `deleteVRFKey`, `ethKeys`, `csaKeys`, `p2pKeys`, `updateUserPassword`), which significantly aids reconnaissance for further attacks against the node's authenticated API surface. It does not by itself grant data access or privilege escalation (actual field resolvers still may enforce their own auth checks), so impact is limited to schema/metadata disclosure — consistent with the "Medium" severity of the original advisory.

### Likelihood Explanation
Likelihood is high for any node with `/query` exposed to the network (default gin route registration, no separate feature flag gating introspection): the endpoint requires no valid session to reach the parser, and the introspection query is a single standard POST request with no special preconditions.

### Recommendation
Explicitly disable introspection in the schema options when not in a debug/insecure mode (e.g., via a validation middleware that rejects `__schema`/`__type` root selections, or a build/config flag that only allows introspection when `Insecure().InfiniteDepthQueries()`-style debug config is set), and/or require `AuthenticateGQL` to fully reject unauthenticated requests before reaching the GraphQL handler rather than silently passing them through. At minimum, fix the discrepancy between the code comment ("Disable introspection...") and the actual implementation which never disables it.

### Proof of Concept
```
POST /query HTTP/1.1
Host: <chainlink-node>
Content-Type: application/json
(no Authorization/session cookie)

{"query":"{ __schema { types { name fields { name } } } queryType { fields { name } } mutationType { fields { name } } } }"}
```
With no valid session cookie set, `AuthenticateGQL` (`core/web/auth/gql.go:25-48`) allows the request through unauthenticated, and `graphqlHandler` (`core/web/router.go:110-134`) processes it via `relay.Handler`, returning the complete schema (all `Query`/`Mutation` field names from `core/web/schema/schema.graphql:10-82`) in the response body.

### Citations

**File:** core/web/router.go (L95-99)
```go
	api.POST("/query",
		auth.AuthenticateGQL(app.AuthenticationProvider(), app.GetLogger().Named("GQLHandler")),
		loader.Middleware(app),
		graphqlHandler(app),
	)
```

**File:** core/web/router.go (L109-127)
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

**File:** core/web/schema/schema.graphql (L10-46)
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
```

**File:** core/web/schema/schema.graphql (L48-82)
```text
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
