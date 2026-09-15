Based on my investigation, I found a concrete analog in the bridge type presenter.

### Title
Bridge outgoing authentication token disclosed to view-only API users via GET /v2/bridge_types - (File: core/web/presenters/bridges.go)

### Summary
The Jenkins advisory concerns a low-privilege ("Extended Read") caller being able to retrieve a credential's encrypted secret material through a read-only API path that should have redacted it. In this Chainlink codebase, `BridgeResource` — the JSONAPI representation returned by the bridge listing/detail endpoints — unconditionally includes the bridge's `OutgoingToken` secret, and that endpoint is explicitly reachable by users holding only the `view` role.

### Finding Description
`BridgeResource.OutgoingToken` has no `omitempty` and is always populated from `bridges.BridgeType.OutgoingToken` by `NewBridgeResource`: [1](#0-0) 

`OutgoingToken` is a generated secret (`utils.NewSecret(24)`), created and persisted alongside the bridge's `IncomingTokenHash`/`Salt`, used to authenticate the node's outgoing callback to the external adapter: [2](#0-1) 

Unlike `IncomingToken`, which is marked `omitempty` and intentionally only surfaced once at creation time, `OutgoingToken` is returned on every subsequent read of the bridge resource — i.e., `GET /v2/bridge_types` and `GET /v2/bridge_types/:name` — with no redaction.

The route-based RBAC test table confirms these GET routes are reachable by `view`-role (read-only) users, not just admin/edit: [3](#0-2) 

The GraphQL resolver path exhibits the identical pattern — `BridgeResolver.OutgoingToken()` unconditionally exposes the value to any authenticated GraphQL query for `Bridge`: [4](#0-3) 

The analogous `ExternalInitiatorResource` presenter has the same issue: `OutgoingToken` is always serialized (no `omitempty`) in the `GET /v2/external_initiators` listing: [5](#0-4) 
and that route is also reachable by `view`-role users per the RBAC table: [6](#0-5) 

### Impact Explanation
A user granted only the lowest "view" role — intended for read-only, non-administrative access — can retrieve the `OutgoingToken` (and, for external initiators, both `OutgoingToken` and implicitly related secrets) for every configured bridge/external initiator, without ever needing "edit" or "admin" permissions. This is precisely the CWE-200/522 pattern in the Jenkins advisory: a low-privilege read path exposes a secret credential that should be redacted after initial issuance, comparable to how `IncomingToken` is correctly treated (`omitempty`, only returned once). Possession of the outgoing token could let a low-privileged, non-admin API user impersonate the Chainlink node's outgoing calls or replay/spoof callback authentication toward the external adapter/initiator, depending on how the token is verified downstream.

### Likelihood Explanation
Likelihood is high for any deployment that grants `view`-level API roles to less-trusted operators/monitoring users (a common, documented, and intended use of the role model) — [7](#0-6)  shows this RBAC model is explicitly tested and expected to be enforced. No special network position or malicious node/peer status is required — this is a plain authenticated (low-privilege) unprivileged-role REST/GraphQL client request.

### Recommendation
Apply the same redaction pattern already used for `IncomingToken`: mark `OutgoingToken` `json:"outgoingToken,omitempty"` in `BridgeResource` and `ExternalInitiatorResource`, and populate it only in the create-response path (as already done for `IncomingToken` in `bridge_types_controller.go`), not in list/get responses. Alternatively, restrict `OutgoingToken` visibility in list/get responses to `admin`/`edit` roles, or redact it (e.g., `"xxxxx"`) in read responses to non-privileged roles, consistent with the secrets-redaction convention already used elsewhere in the config layer (`core/services/chainlink/testdata/secrets-full-redacted.toml`).

### Proof of Concept
1. As an admin, create a bridge via `POST /v2/bridge_types`; note the returned `outgoingToken`.
2. As a `view`-role API user (using an API token/session restricted to `view`), call `GET /v2/bridge_types/<name>` (allowed per `routesRolesMap` entry `{"GET", "/v2/bridge_types/MOCK", true, true, true}`).
3. Observe that the JSON response's `attributes.outgoingToken` field contains the same plaintext secret token created in step 1, disclosed to a role that should not have edit/admin-level credential access.
4. Repeat with `GET /v2/external_initiators` for the equivalent `outgoingToken` field on `ExternalInitiatorResource`.

### Citations

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

**File:** core/bridges/bridge_type.go (L55-102)
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

**File:** core/web/auth/auth_test.go (L203-211)
```go
// Test RBAC (Role based access control) of each route and their required user roles
// Admin is omitted from the fields here since admin should be able to access all routes
type routeRules struct {
	verb               string
	path               string
	viewOnlyAllowed    bool
	editMinimalAllowed bool
	EditAllowed        bool
}
```

**File:** core/web/auth/auth_test.go (L224-224)
```go
	{"GET", "/v2/external_initiators", true, true, true},
```

**File:** core/web/auth/auth_test.go (L227-231)
```go
	{"GET", "/v2/bridge_types", true, true, true},
	{"POST", "/v2/bridge_types", false, false, true},
	{"GET", "/v2/bridge_types/MOCK", true, true, true},
	{"PATCH", "/v2/bridge_types/MOCK", false, false, true},
	{"DELETE", "/v2/bridge_types/MOCK", false, false, true},
```

**File:** core/web/resolver/bridge.go (L52-55)
```go
// OutgoingToken resolves the bridge's outgoing token.
func (r *BridgeResolver) OutgoingToken() string {
	return r.bridge.OutgoingToken
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
