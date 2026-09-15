## Analysis

Confirmed: bridge creation requires only the `edit` role (not `admin`), no URL validation beyond non-empty string, and `BridgeTask` always uses the **unrestricted** HTTP client that has no loopback/RFC1918/link-local egress filtering.

### Title
Non-admin ("edit"-role) user can register a Bridge pointing at an arbitrary internal URL, causing full-response SSRF via BridgeTask - (File: core/services/pipeline/runner.go, core/web/bridge_types_controller.go)

### Summary
`POST /v2/bridge_types` (and the GraphQL `CreateBridge` mutation) is authorized for any user holding the `edit` role — not `admin` — via `auth.RequiresEditRole(bt.Create)`. [1](#0-0)  The handler validates only that the URL string is non-empty; it performs no scheme/host/IP allow-listing. [2](#0-1)  Once persisted, any `BridgeTask` referencing that bridge name is unconditionally wired to `r.unrestrictedHTTPClient` during pipeline initialization, explicitly bypassing the local/private-network egress filter that the `HTTPTask` uses by default. [3](#0-2)  The bridge task then performs a POST to that URL and returns the full response body/telemetry back through the pipeline run, which the same `edit`-role user can read via `GET /v2/jobs/:ID/runs`. [4](#0-3) 

### Finding Description
Two independently-hardened SSRF controls exist elsewhere in the codebase (the `HTTPTask` restricted client blocking loopback/RFC1918/link-local by default, and the Gateway `network.HTTPClient` allowlist for ports/schemes/CIDRs) [5](#0-4) [6](#0-5) . However, the Bridge subsystem deliberately opts out of this protection with the rationale "URL is safe because it comes from the node's own database" [7](#0-6) . That trust assumption breaks down because the `bridge_types` creation endpoint is gated at `edit` role rather than `admin` [1](#0-0) , and `ValidateBridgeType` performs no host/IP restriction on the submitted URL — it only checks for a non-empty string [2](#0-1) . Consequently a lower-privileged, non-admin authenticated user can:
1. Create a bridge (`edit` role) with `url` pointing at `http://169.254.169.254/latest/meta-data/` or `http://127.0.0.1:<internal-port>/...`.
2. Create a job (`edit` role, `POST /v2/jobs`) with a `BridgeTask` referencing that bridge name.
3. Trigger/observe the job run and read the raw response body returned by the internal endpoint via the job-run API/telemetry.

This mirrors the reported MCPHub bug class exactly: an authenticated non-admin actor registers an arbitrary-URL "server"/adapter, causing the hub to issue an unfiltered server-side request and return the response to the caller.

### Impact Explanation
An `edit`-role user (a role explicitly documented as lower privilege than `admin`, intended for job/bridge management, not full node control) can read the contents of internal-only HTTP services reachable from the Chainlink node process — including cloud instance metadata endpoints (credential theft), internal admin panels, or other services bound to loopback/private ranges. This is a full-response (non-blind) SSRF with confidentiality impact, matching the High severity classification of the analog (C:H).

### Likelihood Explanation
High. No special conditions are required beyond having an `edit`-role account (a common non-admin role explicitly designed to be delegated to less-trusted operators for job/bridge management). Creating a bridge and a bridge-task job are both standard, documented workflows requiring no exploitation of any other bug.

### Recommendation
- Enforce IP/host allow-listing (reuse the existing `clhttp` restricted-client / disallowed-IP logic, or the Gateway `AllowedIPsCIDR`-style config) on bridge URLs at creation time in `ValidateBridgeType`, and/or route `BridgeTask` through the restricted HTTP client unless an explicit `admin`-gated "allow unrestricted" flag is set per bridge.
- Alternatively, restrict `POST/PATCH /v2/bridge_types` to `RequiresAdminRole` instead of `RequiresEditRole`, since bridge URLs bypass SSRF protections and this document a real trust boundary between "edit" and "admin".
- Apply the same treatment to the webhook/legacy external-initiator URL fields if any equivalent unrestricted-client path remains reachable by `edit`-role users.

### Proof of Concept
1. As a user with the `edit` role (non-admin), call:
```
POST /v2/bridge_types
{"name":"ssrf-poc","url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/"}
```
2. Create a job with a `BridgeTask`:
```
POST /v2/jobs
{"toml": "type=\"cron\" ... task [type=bridge name=\"ssrf-poc\"]"}
```
3. Trigger the job run and fetch `GET /v2/jobs/:ID/runs/:runID` — the response body of the internal metadata endpoint is returned in the pipeline run result/telemetry, confirming full-response SSRF read by a non-admin authenticated actor.

### Citations

**File:** core/web/router.go (L268-273)
```go
		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))
```

**File:** core/web/bridge_types_controller.go (L35-53)
```go
// ValidateBridgeType checks that the bridge type has the required field with valid values.
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

**File:** core/services/pipeline/runner.go (L341-352)
```go
		case TaskTypeBridge:
			bt := task.(*BridgeTask)
			bt.config = r.config
			bt.bridgeConfig = r.bridgeConfig
			// orm added to BridgeTask
			bt.orm = r.btORM
			bt.specID = spec.ID
			// URL is "safe" because it comes from the node's own database. We
			// must use the unrestrictedHTTPClient because some node operators
			// may run external adapters on their own hardware
			bt.httpClient = r.unrestrictedHTTPClient
			bt.bridgeConnManager = r.bridgeConnManager
```

**File:** core/services/pipeline/task.bridge.go (L242-253)
```go
	var cachedResponse bool
	responseBytes, statusCode, headers, start, finish, err := makeHTTPRequest(requestCtx, lggr, "POST", url, reqHeaders, requestData, t.httpClient, t.config.DefaultHTTPLimit())
	elapsed := finish.Sub(start)
	promBridgeLatency.WithLabelValues(t.Name, statusCodeGroup(statusCode)).Set(elapsed.Seconds())
	promBridgeLatencyHist.WithLabelValues(t.Name, statusCodeGroup(statusCode)).Observe(float64(elapsed.Milliseconds()))

	out := bridgeHTTPOutcome{
		body:           responseBytes,
		statusCode:     statusCode,
		err:            err,
		cachedResponse: false,
	}
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

**File:** core/services/gateway/network/httpclient_test.go (L329-391)
```go
	}{
		{
			name:          "blocked port",
			url:           "http://177.0.0.1:8080",
			expectedError: "port: 8080 not found in allowlist",
			blockPort:     true,
		},
		{
			name:          "blocked scheme",
			url:           "file://127.0.0.1",
			expectedError: "scheme: file not found in allowlist",
		},
		{
			name:          "explicitly blocked IP",
			url:           "http://169.254.0.1",
			expectedError: "ip: 169.254.0.1 not found in allowlist",
		},
		{
			name:          "explicitly blocked IP - internal network",
			url:           "http://169.254.0.1",
			expectedError: "ip: 169.254.0.1 not found in allowlist",
		},
		{
			name:          "explicitly blocked IP - loopback",
			url:           "http://127.0.0.1",
			expectedError: "ip: 127.0.0.1 not found in allowlist",
		},
		{
			name:          "explicitly blocked IP - loopback without scheme",
			url:           "127.0.0.1",
			expectedError: "host:  is not valid",
		},
		{
			name:          "explicitly blocked IP - loopback",
			url:           "https://⑫7.0.0.1",
			expectedError: "ip: 127.0.0.1 not found in allowlist",
		},
		{
			name:          "explicitly blocked IP - loopback shortened",
			url:           "https://127.1",
			expectedError: "no such host",
		},
		{
			name:          "explicitly blocked IP - loopback shortened",
			url:           "https://127.0.1",
			expectedError: "no such host",
		},
		{
			name:          "explicitly blocked IP - loopback hex encoded with separators",
			url:           `https://0x7F.0x00.0x00.0x01`,
			expectedError: "no such host",
		},
		{
			name:          "explicitly blocked IP - loopback octal encoded",
			url:           `https://0177.0000.0000.0001`,
			expectedError: "no such host",
		},
		{
			name:          "explicitly blocked IP - loopback binary encoded",
			url:           `https://01111111.00000000.00000000.00000001`,
			expectedError: "no such host",
		},
		{
```
