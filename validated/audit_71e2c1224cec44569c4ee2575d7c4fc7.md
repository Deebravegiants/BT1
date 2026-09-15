### Title
Bridge OutgoingToken stored and transmitted in plaintext, exposed via viewer-role API to authenticate external adapters - ([File: core/bridges/bridge_type.go])

### Summary
Chainlink stores the `OutgoingToken` for each bridge/external-adapter in the `bridge_types` table as cleartext (not hashed), and returns it unredacted from `GET /v2/bridge_types` and `GET /v2/bridge_types/:name` to any authenticated user holding only the `view` role.

### Finding Description
`BridgeType.OutgoingToken` is generated once and persisted in the DB as a plain string, unlike `IncomingTokenHash`/`Salt`, which are hashed [1](#0-0) . `NewBridgeType` produces this outgoing token in the clear and stores it directly in `BridgeType.OutgoingToken` [2](#0-1) . The ORM inserts and returns the row as-is with no encryption of this field, and `bridge_types.outgoing_token` is stored as plain `text` in the schema [3](#0-2) .

Every read path (`Index`/`Show` controllers) constructs `presenters.NewBridgeResource`, which unconditionally serializes `OutgoingToken` (no `omitempty`, unlike `IncomingToken` which is only set at creation time) [4](#0-3) . `BridgeTypesController.Show`/`Index` call this presenter directly for any successful lookup [5](#0-4) . The GraphQL `Bridge` type likewise always exposes `outgoingToken` [6](#0-5) .

Critically, both `GET /v2/bridge_types` and `GET /v2/bridge_types/:name` are accessible to users with the `view` role (`viewOnlyAllowed: true` in the RBAC route table), not restricted to `admin`/`edit` [7](#0-6) . This means the "Viewer"/read-only role — the lowest-privileged authenticated node user role — can retrieve this credential-like secret for every configured bridge simply by paginating `GET /v2/bridge_types`.

The value returned is a long-lived credential: this exact token is intended to authenticate outgoing requests that the Chainlink node itself makes when calling external adapters that require an outgoing-token header for callback verification (referenced/tested via `X-Chainlink...` headers and consumed by `BridgeTask.Run` when constructing outbound bridge requests via `makeHTTPRequest`) [8](#0-7) . Because it is never rotated automatically and is returned in cleartext on every subsequent read, any low-privilege viewer account (or any actor who compromises a viewer-role API token/session) can exfiltrate it and use it to impersonate the Chainlink node's async/callback channel toward the external adapter, or replay it against the `/v2/resume/:id` async job-resume flow that trusts this shared secret.

### Impact Explanation
Disclosure of the plaintext `OutgoingToken` to a viewer-role (least-privileged) actor allows that actor to impersonate the node when communicating with the configured external adapter's async response/webhook mechanism, potentially forging bridge responses or resuming pending job runs with attacker-controlled data — a request-impersonation / confidentiality breach directly analogous to the Jenkins advisory's "credential visible to users with lesser Extended Read permission" bug class. Impact is scoped to nodes using async bridges with outgoing-token verification, but the credential is exposed to every viewer, not just editors/admins.

### Likelihood Explanation
Likelihood is moderate-to-high in any node granting `view` role accounts (a common minimal-privilege API/UI grant), since exploitation only requires calling an already-authorized, unprivileged GET endpoint — no additional bypass is needed.

### Recommendation
- Do not return `OutgoingToken` in plaintext for `view`-role reads of bridges; treat it like `IncomingToken` (`omitempty`, shown once at creation only) or require `admin`/`edit` role for its retrieval.
- Alternatively, store and validate `OutgoingToken` using a salted hash (mirroring `IncomingTokenHash`) and only reveal the plaintext once, at creation time, similar to `IncomingToken`.
- Support/encourage periodic rotation of `OutgoingToken` via the existing Update endpoint.

### Proof of Concept
1. Create a bridge as an admin: `POST /v2/bridge_types` with a URL, noting `outgoingToken` in the creation response (expected, one-time reveal) [9](#0-8) .
2. Authenticate as a user with only the `view` role.
3. Call `GET /v2/bridge_types` or `GET /v2/bridge_types/{name}` — per the RBAC matrix this succeeds for viewers [7](#0-6) .
4. Observe the response includes the bridge's cleartext `outgoingToken` field, identical to the value generated at creation [10](#0-9) , giving the viewer the credential needed to forge callbacks to that adapter's async response endpoint.

### Citations

**File:** core/bridges/bridge_type.go (L55-68)
```go
// BridgeType is used for external adapters and has fields for
// the name of the adapter and its URL.
type BridgeType struct {
	Name                   BridgeName    `db:"name"`
	URL                    models.WebURL `db:"url"`
	Confirmations          uint32        `db:"confirmations"`
	IncomingTokenHash      string        `db:"incoming_token_hash"`
	Salt                   string        `db:"salt"`
	OutgoingToken          string        `db:"outgoing_token"`
	MinimumContractPayment *assets.Link  `db:"minimum_contract_payment"`
	CreatedAt              time.Time     `db:"created_at"`
	UpdatedAt              time.Time     `db:"updated_at"`
	UseConnectionManager   bool          `db:"use_connection_manager" json:"useConnectionManager"`
}
```

**File:** core/bridges/bridge_type.go (L70-102)
```go
// NewBridgeType returns a bridge type authentication (with plaintext
// password) and a bridge type (with hashed password, for persisting)
func NewBridgeType(btr *BridgeTypeRequest) (*BridgeTypeAuthentication,
	*BridgeType, error,
) {
	incomingToken := utils.NewSecret(24)
	outgoingToken := utils.NewSecret(24)
	salt := utils.NewSecret(24)

	hash, err := incomingTokenHash(incomingToken, salt)
	if err != nil {
		return nil, nil, err
	}

	return &BridgeTypeAuthentication{
		Name:                   btr.Name,
		URL:                    btr.URL,
		Confirmations:          btr.Confirmations,
		IncomingToken:          incomingToken,
		OutgoingToken:          outgoingToken,
		MinimumContractPayment: btr.MinimumContractPayment,
		UseConnectionManager:   btr.UseConnectionManager,
	}, &BridgeType{
		Name:                   btr.Name,
		URL:                    btr.URL,
		Confirmations:          btr.Confirmations,
		IncomingTokenHash:      hash,
		Salt:                   salt,
		OutgoingToken:          outgoingToken,
		MinimumContractPayment: btr.MinimumContractPayment,
		UseConnectionManager:   btr.UseConnectionManager,
	}, nil
}
```

**File:** core/store/migrate/migrations/0001_initial.sql (L132-142)
```sql
CREATE TABLE public.bridge_types (
    name text NOT NULL,
    url text NOT NULL,
    confirmations bigint DEFAULT 0 NOT NULL,
    incoming_token_hash text NOT NULL,
    salt text NOT NULL,
    outgoing_token text NOT NULL,
    minimum_contract_payment character varying(255),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
```

**File:** core/web/presenters/bridges.go (L10-41)
```go
// BridgeResource represents a Bridge JSONAPI resource.
type BridgeResource struct {
	JAID
	Name          string `json:"name"`
	URL           string `json:"url"`
	Confirmations uint32 `json:"confirmations"`
	// The IncomingToken is only provided when creating a Bridge
	IncomingToken          string       `json:"incomingToken,omitempty"`
	OutgoingToken          string       `json:"outgoingToken"`
	MinimumContractPayment *assets.Link `json:"minimumContractPayment"`
	UseConnectionManager   bool         `json:"useConnectionManager"`
	CreatedAt              time.Time    `json:"createdAt"`
}

// GetName implements the api2go EntityNamer interface
func (r BridgeResource) GetName() string {
	return "bridges"
}

// NewBridgeResource constructs a new BridgeResource
func NewBridgeResource(b bridges.BridgeType) *BridgeResource {
	return &BridgeResource{
		// Uses the name as the id...Should change this to the id
		JAID:                   NewJAID(b.Name.String()),
		Name:                   b.Name.String(),
		URL:                    b.URL.String(),
		Confirmations:          b.Confirmations,
		OutgoingToken:          b.OutgoingToken,
		MinimumContractPayment: b.MinimumContractPayment,
		UseConnectionManager:   b.UseConnectionManager,
		CreatedAt:              b.CreatedAt,
	}
```

**File:** core/web/bridge_types_controller.go (L61-109)
```go
func (btc *BridgeTypesController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	btr := &bridges.BridgeTypeRequest{}

	if err := c.ShouldBindJSON(btr); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
	bta, bt, err := bridges.NewBridgeType(btr)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
	if e := ValidateBridgeType(btr); e != nil {
		jsonAPIError(c, http.StatusBadRequest, e)
		return
	}
	orm := btc.App.BridgeORM()
	if e := ValidateBridgeTypeNotExist(ctx, btr, orm); e != nil {
		jsonAPIError(c, http.StatusBadRequest, e)
		return
	}
	if e := orm.CreateBridgeType(ctx, bt); e != nil {
		jsonAPIError(c, http.StatusInternalServerError, e)
		return
	}
	var pgErr *pgconn.PgError
	if errors.As(err, &pgErr) {
		var apiErr error
		if pgErr.ConstraintName == "external_initiators_name_key" {
			apiErr = fmt.Errorf("bridge Type %v conflict", bt.Name)
		} else {
			apiErr = err
		}
		jsonAPIError(c, http.StatusConflict, apiErr)
		return
	}
	resource := presenters.NewBridgeResource(*bt)
	resource.IncomingToken = bta.IncomingToken

	btc.App.GetAuditLogger().Audit(audit.BridgeCreated, map[string]any{
		"bridgeName":                   bta.Name,
		"bridgeConfirmations":          bta.Confirmations,
		"bridgeMinimumContractPayment": bta.MinimumContractPayment,
		"bridgeURL":                    bta.URL,
	})

	jsonAPIResponse(c, resource, "bridge")
}
```

**File:** core/web/bridge_types_controller.go (L112-146)
```go
func (btc *BridgeTypesController) Index(c *gin.Context, size, page, offset int) {
	ctx := c.Request.Context()
	bridges, count, err := btc.App.BridgeORM().BridgeTypes(ctx, offset, size)

	resources := make([]presenters.BridgeResource, 0, len(bridges))
	for _, bridge := range bridges {
		resources = append(resources, *presenters.NewBridgeResource(bridge))
	}

	paginatedResponse(c, "Bridges", size, page, resources, count, err)
}

// Show returns the details of a specific Bridge.
func (btc *BridgeTypesController) Show(c *gin.Context) {
	ctx := c.Request.Context()
	name := c.Param("BridgeName")

	taskType, err := bridges.ParseBridgeName(name)
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	bt, err := btc.App.BridgeORM().FindBridge(ctx, taskType)
	if errors.Is(err, sql.ErrNoRows) {
		jsonAPIError(c, http.StatusNotFound, errors.New("bridge not found"))
		return
	}
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	jsonAPIResponse(c, presenters.NewBridgeResource(bt), "bridge")
}
```

**File:** core/web/schema/type/bridge.graphql (L1-10)
```text
type Bridge {
    id: ID!
    name: String!
    url: String!
    confirmations: Int!
    outgoingToken: String!
    minimumContractPayment: String!
    useConnectionManager: Boolean!
    createdAt: Time!
}
```

**File:** core/web/auth/auth_test.go (L227-230)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/services/pipeline/task.bridge.go (L233-246)
```go
	requestDataJSON, err := t.finalizeAndMarshalBridgeRequestData(lggr, vars, inputValues, &requestData, includeInputAtKey)
	if err != nil {
		return Result{Error: err}, runInfo
	}
	logger.Sugared(lggr).Tracew("Bridge task: sending request",
		"requestData", string(requestDataJSON),
		"url", url.String(),
	)

	var cachedResponse bool
	responseBytes, statusCode, headers, start, finish, err := makeHTTPRequest(requestCtx, lggr, "POST", url, reqHeaders, requestData, t.httpClient, t.config.DefaultHTTPLimit())
	elapsed := finish.Sub(start)
	promBridgeLatency.WithLabelValues(t.Name, statusCodeGroup(statusCode)).Set(elapsed.Seconds())
	promBridgeLatencyHist.WithLabelValues(t.Name, statusCodeGroup(statusCode)).Observe(float64(elapsed.Milliseconds()))
```
