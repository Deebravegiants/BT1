All the claim's key assertions are confirmed by direct code inspection:

- `BridgeResource.OutgoingToken` has no `omitempty` and is unconditionally populated by `NewBridgeResource`, unlike `IncomingToken` which is `omitempty` and only set on `Create`. [1](#0-0) [2](#0-1) 
- `Index` and `Show` both call `presenters.NewBridgeResource` and return it directly without any redaction of `OutgoingToken`. [3](#0-2) 
- The routes `GET /bridge_types` and `GET /bridge_types/:BridgeName` are registered under `authv2` (bare authentication) with no `auth.RequiresEditRole`/`auth.RequiresAdminRole` wrapper, while `POST`/`PATCH`/`DELETE` are wrapped with `auth.RequiresEditRole`. [4](#0-3) 
- `OutgoingToken` is generated with `utils.NewSecret(24)` at bridge creation and stored/copied in plaintext into `BridgeType`, confirming it's a genuine secret. [5](#0-4) 
- `SECURITY.md` does not exclude this class of finding (unprivileged/low-role read access to a real secret is not in the out-of-scope list). [6](#0-5) 

This matches all required validation checks: exact file/line references, a clear broken assumption (routes lack role-gating that other bridge mutation routes have), a reachable path exploitable by a `view`-role authenticated user via a single GET request, and a concrete impact (secret exfiltration usable to impersonate the node's outbound calls to the external adapter) — mapping to the in-scope "key/secret exfiltration" impact category.

Audit Report

## Title
Bridge `OutgoingToken` secret exposed to any authenticated user regardless of role (view-only) - ([File: core/web/bridge_types_controller.go])

## Summary
`BridgeTypesController.Index` and `.Show` return `presenters.BridgeResource`, whose `OutgoingToken` field lacks `omitempty` and is unconditionally populated from the DB-backed `bridges.BridgeType`. The `GET /v2/bridge_types` and `GET /v2/bridge_types/:BridgeName` routes are registered with only bare authentication (no `auth.RequiresEditRole`/`auth.RequiresAdminRole`), so any authenticated user — including the lowest-privilege `view` role — can read every bridge's `OutgoingToken`.

## Finding Description
`NewBridgeResource` copies `b.OutgoingToken` into the JSON:API response unconditionally: [2](#0-1) . The `BridgeResource` struct marks `IncomingToken` as `omitempty` (populated only transiently on `Create`) but gives `OutgoingToken` no such protection: [1](#0-0) . Both `Index` and `Show` return this resource directly to the caller with no field filtering: [3](#0-2) . In `router.go`, `GET /bridge_types` and `GET /bridge_types/:BridgeName` are registered under the generic `authv2` group (authentication only), while the mutating verbs (`POST`, `PATCH`, `DELETE`) are explicitly wrapped with `auth.RequiresEditRole`: [4](#0-3) . This asymmetry means the read paths have no elevated-role check, so any authenticated caller — including `view`-role users — can retrieve the secret. `OutgoingToken` is a genuine credential generated via `utils.NewSecret(24)` and used to authenticate the node's own outbound requests to the external bridge adapter: [5](#0-4) .

## Impact Explanation
An attacker holding a `view`-role API credential (e.g., a read-only monitoring key intentionally provisioned with no write/admin capability) can retrieve every configured bridge's `OutgoingToken` via a single `GET /v2/bridge_types` call. This token authenticates the node's calls to the external adapter, so possessing it lets an attacker impersonate the node's outbound requests to that adapter, potentially manipulating or intercepting the off-chain data feeding the node's job pipelines. This is a concrete secret-exfiltration issue (CWE-200) affecting a role-restricted credential, mapping to the in-scope "key/secret exfiltration" impact class.

## Likelihood Explanation
Exploitation requires only a single authenticated GET request with a valid, even minimally-privileged (`view`) API key — no privilege escalation, race condition, or additional exploit chain is needed. Any deployment issuing `view`-role keys to less-trusted consumers (a common practice for dashboards/monitoring tooling) is directly exposed.

## Recommendation
Gate `OutgoingToken` exposure behind `edit`/`admin` roles: either wrap the `Index`/`Show` handlers with `auth.RequiresEditRole`, or strip/omit `OutgoingToken` from `BridgeResource` for non-privileged callers, mirroring the write-once/`omitempty` treatment already applied to `IncomingToken`.

## Proof of Concept
1. Provision a Chainlink node user/API token with role `view` (lowest privilege tier).
2. As that user, send `GET /v2/bridge_types` (or `GET /v2/bridge_types/:BridgeName` for a known bridge).
3. Observe the JSON:API response body contains `"outgoingToken": "<plaintext secret>"` for each bridge, despite the caller having no edit/admin role, confirming unauthorized secret disclosure via `NewBridgeResource` at [7](#0-6)  and the unguarded route registration at [8](#0-7) .

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

**File:** core/web/presenters/bridges.go (L30-41)
```go
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

**File:** core/web/bridge_types_controller.go (L111-145)
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
```

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/bridges/bridge_type.go (L70-101)
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
```

**File:** SECURITY.md (L1-65)
```markdown
# Common Vulnerability Exclusion List

## Out of Scope & Rules

These are the default impacts recommended to projects to mark as out of scope for their bug bounty program. The actual list of out-of-scope impacts differs from program to program.

### General

- Impacts requiring attacks that the reporter has already exploited themselves, leading to damage.
- Impacts caused by attacks requiring access to leaked keys/credentials.
- Impacts caused by attacks requiring access to privileged addresses (governance, strategist), except in cases where the contracts are intended to have no privileged access to functions that make the attack possible.
- Impacts relying on attacks involving the depegging of an external stablecoin where the attacker does not directly cause the depegging due to a bug in code.
- Mentions of secrets, access tokens, API keys, private keys, etc. in GitHub will be considered out of scope without proof that they are in use in production.
- Best practice recommendations.
- Feature requests.
- Impacts on test files and configuration files, unless stated otherwise in the bug bounty program.

### Smart Contracts / Blockchain DLT

- Incorrect data supplied by third-party oracles.
- Impacts requiring basic economic and governance attacks (e.g. 51% attack).
- Lack of liquidity impacts.
- Impacts from Sybil attacks.
- Impacts involving centralization risks.

Note: This does not exclude oracle manipulation/flash-loan attacks.

### Websites and Apps

- Theoretical impacts without any proof or demonstration.
- Impacts involving attacks requiring physical access to the victim device.
- Impacts involving attacks requiring access to the local network of the victim.
- Reflected plain text injection (e.g. URL parameters, path, etc.).
- This does not exclude reflected HTML injection with or without JavaScript.
- This does not exclude persistent plain text injection.
- Any impacts involving self-XSS.
- Captcha bypass using OCR without impact demonstration.
- CSRF with no state-modifying security impact (e.g. logout CSRF).
- Impacts related to missing HTTP security headers (such as `X-FRAME-OPTIONS`) or cookie security flags (such as `httponly`) without demonstration of impact.
- Server-side non-confidential information disclosure, such as IPs, server names, and most stack traces.
- Impacts causing only the enumeration or confirmation of the existence of users or tenants.
- Impacts caused by vulnerabilities requiring unprompted, in-app user actions that are not part of the normal app workflows.
- Lack of SSL/TLS best practices.
- Impacts that only require DDoS.
- UX and UI impacts that do not materially disrupt use of the platform.
- Impacts primarily caused by browser/plugin defects.
- Leakage of non-sensitive API keys (e.g. Etherscan, Infura, Alchemy, etc.).
- Any vulnerability exploit requiring browser bugs for exploitation (e.g. CSP bypass).
- SPF/DMARC misconfigured records.
- Missing HTTP headers without demonstrated impact.
- Automated scanner reports without demonstrated impact.
- UI/UX best practice recommendations.
- Non-future-proof NFT rendering.

## Prohibited Activities

The following activities are prohibited by default on bug bounty programs on Immunefi. Projects may add further restrictions to their own program.

- Any testing on mainnet or public testnet deployed code; all testing should be done on local forks of either public testnet or mainnet.
- Any testing with pricing oracles or third-party smart contracts.
- Attempting phishing or other social engineering attacks against employees and/or customers.
- Any testing with third-party systems and applications (e.g. browser extensions), as well as websites (e.g. SSO providers, advertising networks).
- Any denial-of-service attacks that are executed against project assets.
- Automated testing of services that generates significant amounts of traffic.
- Public disclosure of an unpatched vulnerability in an embargoed bounty.
```
