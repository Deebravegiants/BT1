Found the key analog. This confirms the design intent: routes `GET /v2/external_initiators` and `GET /v2/bridge_types` are explicitly documented in the RBAC test map as `viewOnlyAllowed: true` [1](#0-0) , i.e., a `view`-role authenticated user (the lowest privilege, read-only role) is intentionally permitted to call these endpoints without hitting `RequiresRunRole`/`RequiresEditRole` gates [2](#0-1) .

Now let's check whether the resource returned to that low-privilege GET actually includes the live `OutgoingToken`/`AccessKey` secrets (as opposed to redacting them), which is the crux of a plaintext-secret-exposure analog to the Jenkins CVE.### Title
Plaintext Bridge/External-Initiator Outgoing Secrets Exposed to Read-Only `view`-Role Users via `GET /v2/bridge_types` and `GET /v2/external_initiators` - (File: core/web/router.go)

### Summary
The Jenkins advisory describes a low-privilege exposure bug class: a secret stored in a config artifact is readable by an actor whose permission level should not grant secret visibility (Extended Read vs. full admin). Chainlink has a structurally analogous pattern: the `BridgeType.OutgoingToken` and `ExternalInitiator.OutgoingToken`/`AccessKey` values are stored and returned in plaintext by the node's REST API, and the routes that return them are explicitly wired to allow the lowest-privilege authenticated role (`view`) to read them.

### Finding Description
`BridgeType.OutgoingToken` is stored unhashed in the database (`outgoing_token text NOT NULL` in the `bridge_types` table) [3](#0-2) , and `NewBridgeType` explicitly keeps the plaintext `OutgoingToken` (unlike `IncomingToken`, which is only hashed/salted) [4](#0-3) . `ExternalInitiator.OutgoingToken`/`OutgoingSecret`/`AccessKey` are similarly stored as plaintext columns [5](#0-4) .

`NewBridgeResource` always serializes `OutgoingToken` into the API resource [6](#0-5) , and `NewExternalInitiatorResource` always serializes `AccessKey`/`OutgoingToken` [7](#0-6) . These are returned unconditionally by the `Index`/`Show` handlers with no role check inside the handler itself [8](#0-7) [9](#0-8) .

Critically, the router wires `GET /v2/external_initiators` and `GET /v2/bridge_types` (and `GET /v2/bridge_types/:BridgeName`) with **no** `auth.RequiresRunRole`/`RequiresEditRole`/`RequiresAdminRole` wrapper — only session/token authentication is required [2](#0-1) . This is confirmed by the project's own RBAC test map, which explicitly documents these GET routes as `viewOnlyAllowed: true`, i.e., intended to be reachable by the lowest-privilege `view` role [1](#0-0) .

### Impact Explanation
Any authenticated node user provisioned with only the `view` role (meant for read-only dashboard/monitoring access, explicitly barred from `RequiresRunRole` actions such as replaying blocks or running jobs — see `RequiresRunRole` at `core/web/auth/auth.go:200-215`) can retrieve the plaintext `OutgoingToken` for every configured bridge and the `AccessKey`/`OutgoingToken` for every external initiator. These tokens authenticate the node when calling out to external adapters/initiators (bridge outgoing token verification, EI outgoing calls). A `view`-role user obtaining these secrets can impersonate the node to the external adapter/initiator or replay outgoing-authenticated calls — a capability well beyond what "read-only" access is meant to permit. This mirrors the Jenkins CVE's core harm: a lower-privileged actor obtaining a live credential intended to be restricted to more privileged operators.

### Likelihood Explanation
Any deployment that provisions `view`-role API users (a supported, documented, lowest-tier role) and has at least one bridge or external initiator configured is affected. No special conditions are required beyond having valid `view`-role credentials and calling `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, or `GET /v2/external_initiators` — this is a single unauthenticated-role HTTP GET reachable from any client with node network access and a low-privilege session/API token. Likelihood is high wherever the `view` role is actually used for restricted third-party or auditor access.

### Recommendation
- Redact `OutgoingToken` (and `AccessKey`/`OutgoingSecret` for external initiators) from `BridgeResource`/`ExternalInitiatorResource` on read (`Index`/`Show`) paths, only surfacing them once at creation time, consistent with how `IncomingToken` is already `omitempty`/creation-only in `BridgeResource` (`core/web/presenters/bridges.go:17`).
- Alternatively, gate `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` behind at least `auth.RequiresRunRole` or `RequiresEditRole`, removing them from the `viewOnlyAllowed` set in `core/web/router.go`.
- Rotate/hash `OutgoingToken` similarly to `IncomingTokenHash`, if outgoing token verification can be redesigned to use HMAC verification rather than plaintext comparison.

### Proof of Concept
1. Provision a Chainlink node user with role `view` (e.g., via `POST /v2/users` as admin, or LDAP/OIDC group mapping to `UserRoleView`).
2. As that user, authenticate a session/API token (`auth.AuthenticateBySession`/`AuthenticateByToken` — no additional role check applied by the route).
3. Call `GET /v2/bridge_types` — response includes `attributes.outgoingToken` for every configured bridge in plaintext (see `presenters.NewBridgeResource`, `core/web/presenters/bridges.go:29-41`, confirmed serialized in `core/web/presenters/bridges_test.go:39-57`).
4. Call `GET /v2/external_initiators` — response includes `attributes.accessKey` and `attributes.outgoingToken` for every external initiator (see `presenters.NewExternalInitiatorResource`, `core/web/presenters/external_initiators.go:67-76`, exercised in `core/web/external_initiators_controller_test.go:104-109`, `125-126`).
5. Use the retrieved `OutgoingToken` to impersonate the node when interacting with the external adapter/initiator endpoint that expects it.

### Citations

**File:** core/web/auth/auth_test.go (L224-230)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/web/router.go (L263-273)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))

		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
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

**File:** core/store/migrate/migrations/0001_initial.sql (L483-495)
```sql
CREATE TABLE public.external_initiators (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone,
    name text NOT NULL,
    url text,
    access_key text NOT NULL,
    salt text NOT NULL,
    hashed_secret text NOT NULL,
    outgoing_secret text NOT NULL,
    outgoing_token text NOT NULL
);
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

**File:** core/web/presenters/bridges.go (L29-41)
```go
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

**File:** core/web/presenters/external_initiators.go (L67-76)
```go
func NewExternalInitiatorResource(ei bridges.ExternalInitiator) ExternalInitiatorResource {
	return ExternalInitiatorResource{
		JAID:          NewJAID(strconv.FormatInt(ei.ID, 10)),
		Name:          ei.Name,
		URL:           ei.URL,
		AccessKey:     ei.AccessKey,
		OutgoingToken: ei.OutgoingToken,
		CreatedAt:     ei.CreatedAt,
		UpdatedAt:     ei.UpdatedAt,
	}
```

**File:** core/web/bridge_types_controller.go (L111-146)
```go
// Index lists Bridges, one page at a time.
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

**File:** core/web/external_initiators_controller.go (L50-59)
```go
func (eic *ExternalInitiatorsController) Index(c *gin.Context, size, page, offset int) {
	ctx := c.Request.Context()
	externalInitiators, count, err := eic.App.BridgeORM().ExternalInitiators(ctx, offset, size)
	resources := make([]presenters.ExternalInitiatorResource, 0, len(externalInitiators))
	for _, initiator := range externalInitiators {
		resources = append(resources, presenters.NewExternalInitiatorResource(initiator))
	}

	paginatedResponse(c, "externalInitiators", size, page, resources, count, err)
}
```
