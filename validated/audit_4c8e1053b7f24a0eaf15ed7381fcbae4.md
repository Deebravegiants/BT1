## Analysis: SSRF Analog via Bridge URL Configuration

The Harbor CVE-2020-13788 describes SSRF where a user who can "edit projects" configures a URL that Harbor's server then fetches, allowing scanning of internal hosts. The chainlink codebase has a directly analogous pattern in bridge management.

### Title
Bridge URL SSRF allows intranet port scanning via unrestricted HTTP client - (File: core/services/pipeline/task.bridge.go)

### Summary
A user with the node's "edit" role can create or update a Bridge (`bridges.BridgeType`) with an arbitrary URL, including internal/intranet hosts (e.g. `http://10.0.0.5:6379`). Unlike the `HTTPTask` pipeline adapter, which defaults to a network-restricted HTTP client (`clhttp.NewRestrictedClient`) that blocks local/private/multicast networks, the `BridgeTask` performs outbound requests to the bridge's stored URL without any such SSRF protection.

### Finding Description
- Bridge creation (`BridgeTypesController.Create` and the GraphQL `CreateBridge`/`UpdateBridge` resolvers) only validates that the bridge name is well-formed and the URL string is non-empty; it does not restrict scheme, host, or IP range. [1](#0-0) [2](#0-1) 
- Test fixtures explicitly confirm internal Docker-network URLs like `http://chainlink_cmc-adapter_1:8080` are accepted as valid bridge URLs. [3](#0-2) 
- `BridgeTask.Run` uses `t.httpClient` (a plain `*http.Client` set via `HelperSetDependencies`) to fetch the bridge's stored URL, with no equivalent of the `allowUnrestrictedNetworkAccess` guard or `safeurl`/`clhttp.ErrDisallowedIP` restriction that the sibling `HTTPTask` enforces. [4](#0-3) 
- By contrast, `HTTPTask.Run` explicitly picks a restricted client for interpolated URLs and surfaces a specific error ("connections to local resources are disabled by default") when it detects `clhttp.ErrDisallowedIP`, demonstrating the project's own recognized SSRF mitigation exists but is not applied to bridges. [5](#0-4) 
- The periodic `bridge_status_reporter` service similarly parses the stored bridge URL and issues GET requests to it/its status path without SSRF filtering, and differentiates error paths (parse error vs. HTTP error vs. non-200 vs. decode error), which can be used as a probing oracle. [6](#0-5) 

### Impact Explanation
A user with node "edit" privileges (the GraphQL mutations require only `authenticateUserCanEdit`, not admin) can register a bridge pointing at any intranet host:port reachable from the Chainlink node, then trigger a job run (or rely on the periodic bridge-status poller) to have the node make the outbound request on their behalf. Differences in response timing, HTTP status, and error messages (connection refused vs. timeout vs. 200) let the attacker fingerprint open ports and reachable services on the node's internal network — the same SSRF/port-scan primitive described in the Harbor advisory.

### Likelihood Explanation
Requires an authenticated user with edit-level access (via the Operator UI or GraphQL API) — not an anonymous or fully unprivileged actor, but a lower privilege tier than node admin/operator key holders. This mirrors the "attacker with ability to edit projects" precondition in the original Harbor CVE. Given that bridge creation is a routine, expected workflow, the barrier to reach this code path is low once edit access is obtained.

### Recommendation
Apply the same restricted-HTTP-client / `safeurl`-style IP/scheme allowlisting used in `task.http.go` and `core/services/gateway/network/httpclient.go` to bridge URL validation (at creation/update time) and/or to the HTTP client used by `BridgeTask.Run` and `bridge_status_reporter.pollBridge`, unless an explicit opt-in flag (mirroring `AllowUnrestrictedNetworkAccess`) is set and audited.

### Proof of Concept
1. As a user with edit permission, call `mutation createBridge` (or `POST /v2/bridge_types`) with `url: "http://169.254.169.254/latest/meta-data/"` or an internal service address/port. [7](#0-6) 
2. Create a job with a `bridge` task referencing that bridge name, or simply wait for `bridge_status_reporter`'s poll cycle.
3. Observe job-run/telemetry output or differing error messages (`Failed to fetch Bridge Status Reporter status` vs. success) to infer whether the target host:port is open, effectively port-scanning the node's intranet — analogous to BIT-harbor-2020-13788.

### Citations

**File:** core/web/bridge_types_controller.go (L36-53)
```go
func ValidateBridgeType(bt *bridges.BridgeTypeRequest) error {
	fe := models.NewJSONAPIErrors()
	if len(bt.Name.String()) < 1 {
		fe.Add("No name specified")
	}
	if _, err := bridges.ParseBridgeName(bt.Name.String()); err != nil {
		fe.Merge(err)
	}
	u := bt.URL.String()
	if len(strings.TrimSpace(u)) == 0 {
		fe.Add("URL must be present")
	}
	if bt.MinimumContractPayment != nil &&
		bt.MinimumContractPayment.Cmp(assets.NewLinkFromJuels(0)) < 0 {
		fe.Add("MinimumContractPayment must be positive")
	}
	return fe.CoerceEmptyToNil()
}
```

**File:** core/web/resolver/mutation.go (L63-99)
```go
func (r *Resolver) CreateBridge(ctx context.Context, args struct{ Input createBridgeInput }) (*CreateBridgePayloadResolver, error) {
	if err := authenticateUserCanEdit(ctx); err != nil {
		return nil, err
	}

	var webURL models.WebURL
	if len(args.Input.URL) != 0 {
		rURL, err := url.ParseRequestURI(args.Input.URL)
		if err != nil {
			return nil, err
		}
		webURL = models.WebURL(*rURL)
	}
	minContractPayment := &assets.Link{}
	if err := minContractPayment.UnmarshalText([]byte(args.Input.MinimumContractPayment)); err != nil {
		return nil, err
	}

	btr := &bridges.BridgeTypeRequest{
		Name:                   bridges.BridgeName(args.Input.Name),
		URL:                    webURL,
		Confirmations:          uint32(max(0, args.Input.Confirmations)),
		MinimumContractPayment: minContractPayment,
		UseConnectionManager:   args.Input.UseConnectionManager != nil && *args.Input.UseConnectionManager,
	}

	bta, bt, err := bridges.NewBridgeType(btr)
	if err != nil {
		return nil, err
	}
	orm := r.App.BridgeORM()
	if err = ValidateBridgeType(btr); err != nil {
		return nil, err
	}
	if err = ValidateBridgeTypeUniqueness(ctx, btr, orm); err != nil {
		return nil, err
	}
```

**File:** core/web/bridge_types_controller_test.go (L62-69)
```go
		{
			"valid docker url",
			bridges.BridgeTypeRequest{
				Name: "adapterwithdockerurl",
				URL:  cltest.WebURL(t, "http://chainlink_cmc-adapter_1:8080"),
			},
			nil,
		},
```

**File:** core/services/pipeline/task.bridge.go (L90-95)
```go
	specID            int32
	orm               bridges.ORM
	config            Config
	bridgeConfig      BridgeConfig
	httpClient        *http.Client
	bridgeConnManager bridgeconn.BridgeConnManager
```

**File:** core/services/pipeline/task.http.go (L97-112)
```go
	requestCtx, cancel := httpRequestCtx(ctx, t, t.config)
	defer cancel()

	var client *http.Client
	if allowUnrestrictedNetworkAccess {
		client = t.unrestrictedHTTPClient
	} else {
		client = t.httpClient
	}
	responseBytes, statusCode, respHeaders, start, finish, err := makeHTTPRequest(requestCtx, lggr, method, url, reqHeaders, requestData, client, t.config.DefaultHTTPLimit())
	elapsed := finish.Sub(start).Milliseconds()
	if err != nil {
		if errors.Is(errors.Cause(err), clhttp.ErrDisallowedIP) {
			err = errors.Wrap(err, `connections to local resources are disabled by default, if you are sure this is safe, you can enable on a per-task basis by setting allowUnrestrictedNetworkAccess="true" in the pipeline task spec, e.g. fetch [type="http" method=GET url="$(decode_cbor.url)" allowUnrestrictedNetworkAccess="true"]`)
		}
		return Result{Error: err}, RunInfo{IsRetryable: isRetryableHTTPError(statusCode, err)}
```

**File:** core/services/nodestatusreporter/bridgestatus/bridge_status_reporter.go (L154-192)
```go
	// Parse bridge URL and construct status endpoint
	parsedURL, err := url.Parse(bridgeURL)
	if err != nil {
		s.handleBridgeError(ctx, bridgeName, jobs, "Failed to parse bridge URL", "bridge", bridgeName, "url", bridgeURL, "error", err)
		return
	}

	// Construct status endpoint URL
	statusURL := &url.URL{
		Scheme: parsedURL.Scheme,
		Host:   parsedURL.Host,
		Path:   path.Join(parsedURL.Path, s.config.StatusPath()),
	}

	// Make HTTP request
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, statusURL.String(), nil)
	if err != nil {
		s.handleBridgeError(ctx, bridgeName, jobs, "Failed to create request for Bridge Status Reporter status", "bridge", bridgeName, "url", statusURL.String(), "error", err)
		return
	}

	resp, err := s.httpClient.Do(req)
	if err != nil {
		s.handleBridgeError(ctx, bridgeName, jobs, "Failed to fetch Bridge Status Reporter status", "bridge", bridgeName, "url", statusURL.String(), "error", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		s.handleBridgeError(ctx, bridgeName, jobs, "Bridge Status Reporter status endpoint returned non-200 status", "bridge", bridgeName, "url", statusURL.String(), "status", resp.StatusCode)
		return
	}

	// Parse response
	var status EAResponse
	if err := json.NewDecoder(resp.Body).Decode(&status); err != nil {
		s.handleBridgeError(ctx, bridgeName, jobs, "Failed to decode Bridge Status Reporter status", "bridge", bridgeName, "url", statusURL.String(), "error", err)
		return
	}
```
