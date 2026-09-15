## Title
Chainlink Bridge Creation Allows Edit-Role Users to Trigger SSRF via Unrestricted HTTP Client - (File: core/services/pipeline/runner.go)

### Summary
A user holding only the `Edit` role (below `Admin`) can create a Bridge pointing to any URL, including internal/private network addresses, through `POST /v2/bridge_types`. Chainlink deliberately routes all bridge-task outbound requests through the *unrestricted* HTTP client rather than the SSRF-protected restricted client used elsewhere in the pipeline, so any job that invokes the bridge will issue an unfiltered outbound request to that URL. This mirrors the reported Budibase bug class: a lower-privileged, non-admin actor supplies an arbitrary URL that is never subjected to SSRF validation, enabling requests to internal infrastructure.

### Finding Description
`POST /v2/bridge_types` is guarded only by `auth.RequiresEditRole`, not `RequiresAdminRole`: [1](#0-0) 

The handler accepts any URL supplied in the request body with no SSRF/host validation — `ValidateBridgeType` only checks that the name is well-formed and the URL string is non-empty: [2](#0-1) 

When a pipeline job later runs a `BridgeTask` referencing that bridge, the runner explicitly wires the bridge task's HTTP client to the **unrestricted** client, bypassing the SSRF-blocking restricted client used for other tasks: [3](#0-2) 

By contrast, the `HTTPTask` (which handles inline `url=` fetches) defaults to the restricted client, which blocks private/local/multicast networks unless `allowUnrestrictedNetworkAccess=true` is explicitly set: [4](#0-3) [5](#0-4) 

The bridge task itself performs no additional URL validation before issuing the request via `makeHTTPRequest`: [6](#0-5) [7](#0-6) 

The same weak-privilege pattern applies to `POST /v2/external_initiators`, which is also gated by `RequiresEditRole` only and stores an arbitrary, unvalidated URL: [8](#0-7) [9](#0-8) 

### Impact Explanation
An Edit-role (non-admin) session or API token holder can create a Bridge whose URL points at internal-only endpoints (cloud metadata services, internal admin APIs, database endpoints on the private network the Chainlink node runs in), then attach that bridge to a job. When the job runs, the node issues an outbound HTTP POST from its own network position to the attacker-chosen target with no IP/scheme allowlist checks, because bridge tasks intentionally use the unrestricted client per the comment in `runner.go`. This can be used to probe or interact with internal services reachable only from the node's network, and the response body is placed directly into the job's pipeline output, which can be surfaced back to the Edit-role user — a direct analog of the Budibase SSRF-with-credential-leakage pattern where a builder-level (non-admin) actor's datasource URL is fetched without SSRF checks and results are returned to the requester.

### Likelihood Explanation
Exploitation only requires an account with the `Edit` role (not `Admin`), which is a normal, lower-privilege operator role in a multi-user Chainlink deployment. Creating a bridge and a job to invoke it is standard, documented functionality — no exploitation of a memory-safety bug or race condition is needed, only intentional use of a documented but security-sensitive design shortcut.

### Recommendation
Apply SSRF validation (the same allow/deny-list mechanism used by the restricted HTTP client for `HTTPTask`) to bridge and external-initiator URLs, or at minimum restrict bridge creation/update to `Admin` role given the unrestricted network access it grants at execution time. Consider adding an explicit, admin-approved allowlist for bridge target hosts, and avoid echoing the raw upstream response to lower-privileged Edit users when the bridge target was not admin-approved.

### Proof of Concept
1. Authenticate as a user/API token with role `Edit` (not `Admin`).
2. `POST /v2/bridge_types` with `{"name":"evil","url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/"}` — succeeds because only `RequiresEditRole` is enforced and `ValidateBridgeType` performs no SSRF/host checks.
3. `POST /v2/jobs` with a TOML pipeline spec containing `fetch [type=bridge name="evil" requestData="{}"]`.
4. Trigger the job run; `runner.go`'s `InitializePipeline` assigns `bt.httpClient = r.unrestrictedHTTPClient` for the `BridgeTask`, so the outbound POST to the internal URL is sent with no SSRF filtering.
5. Observe the pipeline task result/response body returned to the Edit-role user, containing data from the internal endpoint.

### Citations

**File:** core/web/router.go (L263-266)
```go
		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))
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

**File:** core/services/pipeline/task.http.go (L97-113)
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
	}
```

**File:** core/services/pipeline/task.http_test.go (L206-251)
```go
func TestHTTPTask_OverrideURLSafe(t *testing.T) {
	t.Parallel()

	config := configtest.NewTestGeneralConfig(t)
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, err := w.Write([]byte("{}"))
		assert.NoError(t, err)
	})

	server := httptest.NewServer(handler)
	defer server.Close()

	task := pipeline.HTTPTask{
		Method:      "POST",
		URL:         server.URL,
		RequestData: ethUSDPairing,
	}
	// Use real clients here to actually test the local connection blocking
	r := clhttp.NewRestrictedClient(config.Database(), logger.TestLogger(t))
	u := clhttp.NewUnrestrictedClient()
	task.HelperSetDependencies(config.JobPipeline(), r, u)

	result, runInfo := task.Run(t.Context(), logger.TestLogger(t), pipeline.NewVarsFrom(nil), nil)
	assert.False(t, runInfo.IsPending)
	assert.False(t, runInfo.IsRetryable)
	require.NoError(t, result.Error)

	task.URL = "$(url)"

	vars := pipeline.NewVarsFrom(map[string]any{"url": server.URL})
	result, runInfo = task.Run(t.Context(), logger.TestLogger(t), vars, nil)
	assert.False(t, runInfo.IsPending)
	assert.True(t, runInfo.IsRetryable)
	require.Error(t, result.Error)
	require.Contains(t, result.Error.Error(), "Connections to local/private and multicast networks are disabled")
	require.Nil(t, result.Value)

	task.AllowUnrestrictedNetworkAccess = "true"

	result, runInfo = task.Run(t.Context(), logger.TestLogger(t), vars, nil)
	assert.False(t, runInfo.IsPending)
	assert.False(t, runInfo.IsRetryable)
	require.NoError(t, result.Error)
}
```

**File:** core/services/pipeline/task.bridge.go (L242-246)
```go
	var cachedResponse bool
	responseBytes, statusCode, headers, start, finish, err := makeHTTPRequest(requestCtx, lggr, "POST", url, reqHeaders, requestData, t.httpClient, t.config.DefaultHTTPLimit())
	elapsed := finish.Sub(start)
	promBridgeLatency.WithLabelValues(t.Name, statusCodeGroup(statusCode)).Set(elapsed.Seconds())
	promBridgeLatencyHist.WithLabelValues(t.Name, statusCodeGroup(statusCode)).Observe(float64(elapsed.Milliseconds()))
```

**File:** core/services/pipeline/common_http.go (L38-44)
```go
	var request *http.Request
	request, err = http.NewRequestWithContext(ctx, string(method), url.String(), bodyReader)
	if err != nil {
		err = errors.Wrap(err, "failed to create http.Request")
		return responseBytes, statusCode, respHeaders, start, finish, err
	}
	request.Header.Set("Content-Type", "application/json")
```

**File:** core/web/external_initiators_controller.go (L61-90)
```go
// Create builds and saves a new external initiator
func (eic *ExternalInitiatorsController) Create(c *gin.Context) {
	ctx := c.Request.Context()
	eir := &bridges.ExternalInitiatorRequest{}
	if !eic.App.GetConfig().JobPipeline().ExternalInitiatorsEnabled() {
		err := errors.New("The External Initiator feature is disabled by configuration")
		jsonAPIError(c, http.StatusMethodNotAllowed, err)
		return
	}

	eia := auth.NewToken()
	if err := c.ShouldBindJSON(eir); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	ei, err := bridges.NewExternalInitiator(eia, eir)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	if err := ValidateExternalInitiator(ctx, eir, eic.App.BridgeORM()); err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}
	if err := eic.App.BridgeORM().CreateExternalInitiator(ctx, ei); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
```
