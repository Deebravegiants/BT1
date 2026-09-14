### Title
Unprivileged "view"-role users can read plaintext `OutgoingToken` webhook credentials for all Bridges and External Initiators via `GET /v2/bridge_types` and `GET /v2/external_initiators` - (File: `core/web/presenters/external_initiators.go`, `core/web/presenters/bridges.go`)

### Summary
The RKE advisory describes a class of bug where sensitive operational credentials (SSH keys, cloud credentials, encryption keys) needed to administer a system are bundled into a state object that is readable by users who only have low-privilege read access, thereby granting them effectively higher-privilege capability (impersonation/administration). The chainlink analog is narrower in scope but matches the same bug class: node-side webhook/bridge "outgoing" credentials (`OutgoingToken`) are stored and returned in full, in plaintext, by list/show endpoints that are accessible to the lowest read-only web UI/API role (`view`), rather than being restricted to `admin`/`edit` or shown only once at creation time like the corresponding `IncomingToken`.

### Finding Description
The `BridgeType` and `ExternalInitiator` domain objects store two distinct token/secret pairs:
- `IncomingTokenHash`/salt (hashed) for authenticating requests coming *into* the node from adapters/external initiators.
- `OutgoingToken` (and `OutgoingSecret` for external initiators) stored and returned in **plaintext**, used to authenticate the node's outbound calls *to* the adapter/external initiator. [1](#0-0) [2](#0-1) 

Unlike `IncomingToken`, which is only returned once at creation time (`omitempty` json tag, only populated by `NewBridgeResource`'s creation path), `OutgoingToken` is unconditionally serialized in the resource presenters used by both the `Index` (list) and `Show` handlers: [3](#0-2) [4](#0-3) 

These endpoints are registered with authentication but **without** any elevated-role requirement — only `Create`/`Update`/`Destroy` require `RequiresEditRole`, while `Index`/`Show` (GET) allow any authenticated role, including the read-only `view` role: [5](#0-4) 

This is explicitly confirmed by the RBAC test matrix, which marks `GET /v2/external_initiators` and `GET /v2/bridge_types` (and `GET /v2/bridge_types/MOCK`) as `viewOnlyAllowed = true`: [6](#0-5) 

The same field is also exposed unauthenticated-role-gated via GraphQL (`Bridge.outgoingToken`), reachable by any authenticated GraphQL user through `authenticateUser(ctx)` without a role check: [7](#0-6) 

### Impact Explanation
Any user provisioned with the lowest privilege level (`view`) in the node's RBAC system can enumerate all configured Bridges and External Initiators and retrieve their plaintext `OutgoingToken`/`OutgoingSecret` values. These tokens are credentials the node uses to authenticate itself when calling out to external adapters/initiators. A view-only user obtaining these tokens could impersonate the Chainlink node when communicating with those external services (forging responses, spoofing calls, or replaying/crafting requests that the external service trusts as originating from the node), which is a horizontal privilege escalation from "read-only" to "credential holder" — directly analogous to the RKE issue where a low-privileged reader of a state object gains admin-equivalent credentials.

### Likelihood Explanation
Likelihood is moderate: it requires an attacker to already hold a valid `view`-role API/session credential on the target chainlink node (an "unprivileged" but still authenticated actor per the RBAC model), which is a normal, commonly-provisioned role for auditors/monitoring users. No additional bypass is needed — the exposure is by design of the current route/role wiring and presenter serialization, so any legitimate `view` account (or a session/token narrowly intended for read-only dashboards) can pull these credentials with a single unauthenticated-role-gated GET request.

### Recommendation
- Do not return `OutgoingToken`/`OutgoingSecret` in `Index`/`Show` responses for bridges and external initiators; treat them like `IncomingToken` — return once at creation only, and redact (`"xxxxx"`/omit) on subsequent reads.
- If outgoing token visibility is required for operational reasons, gate `GET /v2/bridge_types`, `GET /v2/bridge_types/:BridgeName`, and `GET /v2/external_initiators` (and the GraphQL `Bridge.outgoingToken`/initiator equivalents) behind `auth.RequiresEditRole` or `auth.RequiresAdminRole` instead of allowing any authenticated role.
- Apply the same redaction pattern already used for TOML secrets (`core/store/models/secrets.go`, `SecretString` → `"xxxxx"`) to these presenter structs.

### Proof of Concept
1. Provision a chainlink node user with role `view` (lowest privilege, e.g., a read-only dashboard account).
2. As that user, authenticate and call:
   - `GET /v2/bridge_types` → response includes `outgoingToken` field in plaintext for every configured bridge.
   - `GET /v2/external_initiators` → response includes `outgoingToken` (and, at the ORM layer, `outgoingSecret`) in plaintext for every configured external initiator.
3. Confirmed by the existing test asserting `view` role is permitted on these routes (`viewOnlyAllowed = true`) at [6](#0-5)  and by the test that asserts `OutgoingToken` is present in the `/v2/external_initiators` list response body at [8](#0-7) .
4. Use the retrieved `OutgoingToken` to authenticate as the node against the external adapter/initiator endpoint, impersonating the node's outbound calls.

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

**File:** core/bridges/external_initiator.go (L21-34)
```go
// ExternalInitiator represents a user that can initiate runs remotely
type ExternalInitiator struct {
	ID             int64
	Name           string
	URL            *models.WebURL
	AccessKey      string
	Salt           string
	HashedSecret   string
	OutgoingSecret string
	OutgoingToken  string

	CreatedAt time.Time
	UpdatedAt time.Time
}
```

**File:** core/web/presenters/bridges.go (L10-22)
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
```

**File:** core/web/presenters/external_initiators.go (L57-77)
```go
type ExternalInitiatorResource struct {
	JAID
	Name          string         `json:"name"`
	URL           *models.WebURL `json:"url"`
	AccessKey     string         `json:"accessKey"`
	OutgoingToken string         `json:"outgoingToken"`
	CreatedAt     time.Time      `json:"createdAt"`
	UpdatedAt     time.Time      `json:"updatedAt"`
}

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
}
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

**File:** core/web/auth/auth_test.go (L224-231)
```go
	{"GET", "/v2/external_initiators", true, true, true},
	{"POST", "/v2/external_initiators", false, false, true},
	{"DELETE", "/v2/external_initiators/MOCK", false, false, true},
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** deployment/environment/web/sdk/internal/schema.graphql (L118-126)
```text
type Bridge {
    id: ID!
    name: String!
    url: String!
    confirmations: Int!
    outgoingToken: String!
    minimumContractPayment: String!
    createdAt: Time!
}
```

**File:** core/web/external_initiators_controller_test.go (L104-126)
```go
	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiBar.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiBar.Name, externalInitiators[0].Name)
	assert.Nil(t, externalInitiators[0].URL)
	assert.Equal(t, eiBar.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiBar.OutgoingToken, externalInitiators[0].OutgoingToken)

	resp, cleanup = client.Get(links["next"].Href)
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusOK)

	externalInitiators = []presenters.ExternalInitiatorResource{}
	err = web.ParsePaginatedResponse(cltest.ParseResponseBody(t, resp), &externalInitiators, &links)
	require.NoError(t, err)
	assert.Empty(t, links["next"])
	assert.NotEmpty(t, links["prev"])

	assert.Len(t, externalInitiators, 1)
	assert.Equal(t, strconv.FormatInt(eiFoo.ID, 10), externalInitiators[0].ID)
	assert.Equal(t, eiFoo.Name, externalInitiators[0].Name)
	assert.Equal(t, eiFoo.URL.String(), externalInitiators[0].URL.String())
	assert.Equal(t, eiFoo.AccessKey, externalInitiators[0].AccessKey)
	assert.Equal(t, eiFoo.OutgoingToken, externalInitiators[0].OutgoingToken)
```
