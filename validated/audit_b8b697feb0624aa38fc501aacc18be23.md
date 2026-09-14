## Title
SSRF via unvalidated HTTP redirects in workflow artifact fetcher, exploitable by an unprivileged workflow owner — (File: `core/services/workflows/syncer/v2/fetcher.go`)

### Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds a plain `http.Client{Timeout: 30 * time.Second}` with no `CheckRedirect` set, so Go's default client will transparently follow up to 10 redirects to *any* host/scheme returned in a response's `Location` header [1](#0-0) . This client fetches workflow binary/config artifacts from URLs supplied by the on-chain `WorkflowRegistry` contract's `BinaryURL`/`ConfigURL` fields, which are set by whoever calls `UpsertWorkflow` — an unprivileged workflow owner [2](#0-1) [3](#0-2) . This is the same bug class as the Trail of Bits finding against the price-feeder: an attacker-influenced upstream endpoint issues an HTTP redirect that the vulnerable client blindly follows, potentially reaching internal-only services.

### Finding Description
`FetcherService`/`NewFetcherFunc` chooses `newHTTPFetcher` whenever the artifact base URL scheme is `http`/`https` [4](#0-3) . Inside `newHTTPFetcher`, the constructed `http.Client` has only a `Timeout` set — `CheckRedirect` is left at its Go default (`nil`), meaning redirects are followed automatically, unlike the pattern used elsewhere in the codebase (e.g. `core/services/gateway/network/httpclient.go`, which explicitly sets `SetCheckRedirect(disableRedirects)` together with an IP/port allowlist via `safeurl`) [5](#0-4) , and the `DirectHTTPAction`/`DirectConfidentialHTTPAction` fakes, which also explicitly call `disableRedirects` [6](#0-5) .

The `BinaryURL`/`ConfigURL` values driving this fetch originate from the `WorkflowRegisteredEvent` payload, which is populated straight from the on-chain `WorkflowRegistry` contract's `UpsertWorkflow` call [7](#0-6) . Registering a workflow (calling `UpsertWorkflow` with an arbitrary `binaryURL`/`configURL`) is an action available to any workflow owner — an unprivileged, external actor from the node's perspective — as shown by the test harness that drives this exact call path [8](#0-7) .

When the Chainlink node's syncer processes a `WorkflowRegisteredEvent`, it calls `FetchWorkflowArtifacts(ctx, wfID, payload.BinaryURL, payload.ConfigURL)` [9](#0-8) , which — unless the URL host matches the configured `ArtifactStorageHost` (in which case a signed storage URL is substituted) — dispatches the fetch through `h.fetchFn`, i.e. the vulnerable `newHTTPFetcher` client, directly to the attacker-supplied host.

### Impact Explanation
An attacker who controls (or can make respond arbitrarily) the host referenced by `BinaryURL`/`ConfigURL` can return an HTTP redirect (e.g. `301 Location: http://127.0.0.1:6688/...` or a cloud metadata endpoint `http://169.254.169.254/...`) and force the node's fetcher to issue a follow-up request to that internal address with no scheme/host/IP restriction — the exact SSRF pattern described in the report ("attacker gains control over the API... redirects to a local address... providing access to restricted services"). Depending on what is reachable, this can be used for internal service discovery/probing, or interaction with unauthenticated local APIs, without needing any authentication credential from the node operator.

### Likelihood Explanation
Likelihood is Low-to-Medium: the attacker needs to control (or man-in-the-middle/compromise) the artifact host referenced by their own `BinaryURL`, which they fully choose when registering the workflow — this is trivial to satisfy since the workflow owner supplies the URL themselves. The primary constraint is that if the host matches the configured `ArtifactStorageHost`, a signed URL from the trusted storage service is substituted instead of the raw attacker URL, bypassing the vulnerable path; however any *other* host is fetched directly via the unprotected client.

### Recommendation
Set `CheckRedirect` on the `http.Client` in `newHTTPFetcher` to disable redirects (mirroring `disableRedirects` used in `core/services/gateway/network/httpclient.go` and `core/capabilities/fakes/http_action.go`), or at minimum re-validate any redirect target against the same IP/host allowlist and scheme restrictions applied to the initial request before following it.

### Proof of Concept
1. Attacker stands up `http://attacker.example/binary` that responds with `301 Moved Permanently` and `Location: http://127.0.0.1:6688/v2/keys` (or any internal-only endpoint reachable from the node).
2. Attacker calls `WorkflowRegistry.UpsertWorkflow(...)` with `BinaryURL = "http://attacker.example/binary"`.
3. The node's `eventHandler.workflowRegisteredEvent` → `createWorkflowSpec` → `Store.FetchWorkflowArtifacts` → `newHTTPFetcher` issues the request; because `CheckRedirect` is unset, Go's `http.Client` automatically follows the redirect to the internal address, and the response is treated as workflow binary bytes (fetch will typically fail base64-decoding, but the outbound internal request has already been made, confirming SSRF/probing capability).

### Citations

**File:** core/services/workflows/syncer/v2/fetcher.go (L172-196)
```go
// NewFetcher creates a new FetcherFunc based on the provided URL configuration
// The implementation supports both file and HTTP(S) URLs and bypasses the gateway
func NewFetcherFunc(baseURL string, lggr logger.Logger) (types.FetcherFunc, error) {
	if baseURL == "" {
		return nil, errors.New("baseURL cannot be empty")
	}

	u, err := url.Parse(baseURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	switch u.Scheme {
	case "file":
		// Ensure the basePath is absolute
		if !filepath.IsAbs(u.Path) {
			return nil, fmt.Errorf("basePath must be an absolute path, got: %s", u.Path)
		}
		return newFileFetcher(u.Path, lggr), nil
	case "http", "https":
		return newHTTPFetcher(baseURL, lggr), nil
	default:
		return nil, fmt.Errorf("unsupported URL scheme: %s", u.Scheme)
	}
}
```

**File:** core/services/workflows/syncer/v2/fetcher.go (L243-272)
```go
func newHTTPFetcher(baseURL string, lggr logger.Logger) types.FetcherFunc {
	client := &http.Client{
		Timeout: 30 * time.Second,
	}

	return func(ctx context.Context, messageID string, req ghcapabilities.Request) ([]byte, error) {
		// Clean the path to prevent directory traversal
		cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")

		// Join base URL with path
		u, err := url.Parse(baseURL)
		if err != nil {
			return nil, fmt.Errorf("failed to parse base URL: %w", err)
		}

		u.Path = filepath.Join(u.Path, cleanPath)
		fetchURL := u.String()

		lggr.Debugw("Fetching HTTP resource", "url", fetchURL, "workflowID", req.WorkflowID)

		req2, err := http.NewRequestWithContext(ctx, http.MethodGet, fetchURL, nil)
		if err != nil {
			return nil, fmt.Errorf("failed to create request: %w", err)
		}

		resp, err := client.Do(req2)
		if err != nil {
			return nil, fmt.Errorf("HTTP request failed: %w", err)
		}
		defer resp.Body.Close()
```

**File:** core/services/workflows/syncer/v2/handler.go (L781-801)
```go
func (h *eventHandler) createWorkflowSpec(ctx context.Context, payload WorkflowRegisteredEvent) (*job.WorkflowSpec, error) {
	ctx, span := h.tracer.Start(ctx, "fetch_artifacts",
		trace.WithAttributes(
			attribute.String("component", "workflow_syncer"),
			attribute.String("workflow_name", payload.WorkflowName),
		))
	defer span.End()

	wfID := payload.WorkflowID.Hex()
	owner := hex.EncodeToString(payload.WorkflowOwner)
	orgID, err := h.fetchOrganizationID(ctx, owner)
	if err != nil {
		h.lggr.Warnw("Failed to get organization from linking service", "workflowOwner", owner, "error", err)
	}
	ctx = contexts.WithCRE(ctx, contexts.CRE{Org: orgID, Owner: owner, Workflow: wfID})

	// With Workflow Registry contract v2 the BinaryURL and ConfigURL are expected to be identifiers that put through the Storage Service.
	decodedBinary, config, err := h.workflowArtifactsStore.FetchWorkflowArtifacts(ctx, wfID, payload.BinaryURL, payload.ConfigURL)
	if err != nil {
		return nil, err
	}
```

**File:** system-tests/lib/cre/workflow/workflow.go (L238-275)
```go
// registerWorkflow handles workflow registration for registry contracts
func registerWorkflow(
	sc *seth.Client,
	workflowRegistryAddr common.Address,
	version *semver.Version,
	donFamily, workflowName, workflowID, workflowTag, binaryURL, configURL string,
	attributes []byte,
) error {
	registry, err := getRegistryInstance(sc, workflowRegistryAddr, version)
	if err != nil {
		return err
	}

	// Check and link owner if needed using existing helper function
	if verifyErr := verifyOwnerLinkedWithRegistry(registry, sc, workflowName); verifyErr != nil {
		// If owner is not linked, try to link them
		if linkErr := LinkOwner(sc, workflowRegistryAddr, version); linkErr != nil {
			return errors.Wrap(linkErr, "failed to link owner to org")
		}
	}

	if donFamily == "" {
		return errors.New("donFamily is required for workflow registration")
	}

	// Register workflow
	_, err = sc.Decode(registry.UpsertWorkflow(
		sc.NewTXOpts(),
		workflowName,
		workflowTag,
		[32]byte(common.Hex2Bytes(workflowID)),
		defaultWorkflowStatus,
		donFamily,
		binaryURL,
		configURL,
		attributes,
		false,
	))
```

**File:** core/services/gateway/network/httpclient.go (L283-292)
```go
	safeConfigBuilder := safeurl.
		GetConfigBuilder().
		SetAllowedIPs(config.AllowedIPs...).
		SetAllowedIPsCIDR(config.AllowedIPsCIDR...).
		SetAllowedPorts(config.AllowedPorts...).
		SetAllowedSchemes(config.AllowedSchemes...).
		SetBlockedIPs(config.BlockedIPs...).
		SetBlockedIPsCIDR(config.BlockedIPsCIDR...).
		SetCheckRedirect(disableRedirects).
		SetTransport(defaultTransport)
```

**File:** core/capabilities/fakes/http_action.go (L192-203)
```go
func disableRedirects(*http.Request, []*http.Request) error {
	return errRedirectsDisabled
}

// newHTTPClient builds the HTTP client used to make the outbound request. When
// the request carries mTLS auth, the client is configured to present the
// supplied certificate and private key as a client certificate.
func newHTTPClient(input *customhttp.Request, timeout time.Duration) (*http.Client, error) {
	client := &http.Client{
		Timeout:       timeout,
		CheckRedirect: disableRedirects,
	}
```

**File:** core/services/workflows/artifacts/v2/store.go (L131-183)
```go
func (h *Store) FetchWorkflowArtifacts(ctx context.Context, workflowID, binaryURL, configURL string) ([]byte, []byte, error) {
	// Check if the workflow spec is already stored in the database.
	// A row whose binary payload is empty is a pause tombstone - don't use it.
	if spec, err := h.orm.GetWorkflowSpec(ctx, workflowID); err == nil && spec.Workflow != "" {
		// there is no update in the BinaryURL or ConfigURL, lets decode the stored artifacts
		decodedBinary, err := hex.DecodeString(spec.Workflow)
		if err != nil {
			return nil, nil, fmt.Errorf("failed to decode stored workflow spec: %w", err)
		}
		return decodedBinary, []byte(spec.Config), nil
	}

	// Determine which URL to retrieve workflow binary artifacts from
	parsedBinaryURL, err := url.Parse(binaryURL)
	if err != nil {
		return nil, nil, fmt.Errorf("invalid binary URL: %w", err)
	}

	// If the binary URL points to the artifact storage host, use the retrieve function to get the signed URL.
	// NOTE: retrieveFunc may be nil if the fetcherFunc was overridden.
	// TODO CRE-632: retrieverFunc should enforced made to always be set, once local CRE can support it.
	if h.retrieveFunc != nil && parsedBinaryURL.Host == h.config.ArtifactStorageHost {
		signedBinaryURL, err2 := h.retrieveFunc(ctx, &storage_service.DownloadArtifactRequest{
			Id:   workflowID,
			Type: storage_service.ArtifactType_ARTIFACT_TYPE_BINARY,
		})
		if err2 != nil {
			return nil, nil, fmt.Errorf("failed to get binary artifact URL: %w", err2)
		}
		binaryURL = signedBinaryURL
	}

	// Fetch the binary files from the specified URLs.
	var (
		binary, decodedBinary, config []byte
	)

	maxBinarySize, err := h.limiters.MaxBinarySize.Limit(ctx)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to get binary size limit: %w", err)
	} else if maxBinarySize < 0 {
		maxBinarySize = 0
	}
	req := ghcapabilities.Request{
		URL:              binaryURL,
		Method:           http.MethodGet,
		MaxResponseBytes: safeUint32(uint64(maxBinarySize)),
		WorkflowID:       workflowID,
	}
	binary, err = h.fetchFn(ctx, messageID(binaryURL, workflowID), req)
	if err != nil {
		return nil, nil, &types.ArtifactFetchError{ArtifactType: "binary", URL: binaryURL, Err: err}
	}
```
