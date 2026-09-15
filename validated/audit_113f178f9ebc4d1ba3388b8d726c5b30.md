### Title
Workflow-Registry Artifact Fetcher Bypasses SSRF Protections via Unvalidated Redirect-Following HTTP Client - (File: core/services/workflows/syncer/v2/fetcher.go)

### Summary
The `newHTTPFetcher` used by `NewFetcherFunc` in the local/direct workflow-artifact fetcher path constructs a bare `*http.Client` with no SSRF protections (no IP/port/scheme allowlisting, no redirect blocking), in contrast to the gateway's `network.HTTPClient`, which explicitly blocks redirects (`disableRedirects`) and enforces IP/port/scheme allowlists via `safeurl` [1](#0-0) .

### Finding Description
`NewFetcherFunc` dispatches to `newHTTPFetcher` for `http`/`https` base URLs [2](#0-1) . `newHTTPFetcher` builds requests by joining the configured base URL with `req.URL` (attacker/workflow-registry-controlled path input) and issues them with a default `http.Client{Timeout: 30 * time.Second}` [3](#0-2) . Go's default `http.Client` follows redirects (up to 10) with no host/IP restrictions, and there is no scheme/IP/port allowlist logic here at all — unlike the gateway's outbound HTTP path in `core/services/gateway/network/httpclient.go`, which uses `safeurl` and a custom `CheckRedirect` (`disableRedirects`) to block private/link-local IPs, disallowed schemes/ports, and any redirect hop [4](#0-3) .

This fetcher is reached from `Store.FetchWorkflowArtifacts`, which fetches workflow binary/config artifacts from `BinaryURL`/`ConfigURL` values that originate in `WorkflowRegisteredEvent` — i.e., data supplied by whoever registers a workflow on-chain (an otherwise unprivileged/external actor relative to node infrastructure) [5](#0-4) [6](#0-5) .

However, I could not confirm that `newHTTPFetcher` is actually wired into the production node's default workflow-registry sync path. The primary production path (`newFetcherServiceV2` in `core/services/cre/cre.go`) uses `FetcherService.Fetch`, which routes requests through the gateway's `OutgoingConnectorHandler`/DON gateway (the SSRF-protected path) rather than `NewFetcherFunc` [7](#0-6) . `NewFetcherFunc`/`newHTTPFetcher` appears reachable only via `Opts.FetcherFunc` overrides (used in tests and possibly local-CRE/dev tooling in `core/cmd/shell.go`), and I was not able to fully trace whether any production/unprivileged-reachable code path assigns `NewFetcherFunc`'s output as the live `Opts.FetcherFunc` for a real node deployment.

### Impact Explanation
If `newHTTPFetcher` is used in a reachable production configuration, a malicious workflow owner could set `BinaryURL`/`ConfigURL` to an attacker-controlled server that responds with a 3xx redirect to an internal address (e.g., cloud metadata endpoint, internal admin API), and the unprotected `http.Client` would follow it, causing the node to make requests to internal-only resources and potentially leak response content back into stored workflow specs. This matches CWE-918 (SSRF) impact.

### Likelihood Explanation
Uncertain/Low-to-Medium: the vulnerable code exists and is unguarded, but its reachability from unprivileged workflow-registration in the default node deployment could not be confirmed with available tooling — the primary node flow (`newFetcherServiceV2`) uses the SSRF-hardened gateway client, not `newHTTPFetcher`. This function is documented as bypassing the gateway ("bypasses the gateway") and appears intended for local/dev/file-serving use cases where the operator supplies the trusted base URL, which would reduce the practical attacker surface.

### Recommendation
Regardless of current wiring, harden `newHTTPFetcher` to match the gateway's protections: disable automatic redirect following (or validate each redirect target) and apply IP/port/scheme allowlisting consistent with `core/services/gateway/network/httpclient.go`'s `safeurl`-based validation, before this function can safely be exposed to any externally/workflow-supplied URL segment.

### Proof of Concept
Not constructed — reachability from an unprivileged/external actor in the shipped node's default configuration could not be confirmed with available tools; this would require live tracing of `Opts.FetcherFunc` assignment paths in `core/cmd/shell.go` and deployment configuration to confirm `newHTTPFetcher` is actually invoked outside of tests.

### Citations

**File:** core/services/gateway/network/httpclient.go (L354-399)
```go
func disableRedirects(req *http.Request, via []*http.Request) error {
	return &redirectsDisabledError{}
}

type redirectsDisabledError struct{}

func (e *redirectsDisabledError) Error() string { return "redirects are not allowed" }

func truncateLogError(err error) error {
	var urlErr *url.Error
	if !errors.As(err, &urlErr) {
		return err
	}
	u, parseErr := url.Parse(urlErr.URL)
	if parseErr != nil {
		return urlErr.Err
	}
	// trim to scheme + host only
	sanitized := &url.Error{Op: urlErr.Op, URL: u.Scheme + "://" + u.Host, Err: urlErr.Err}
	return sanitized
}

// isBlockedRequest checks if an error is caused by blocked/invalid input (e.g., blocked IP, invalid scheme, blocked headers)
// It checks for safeurl typed errors.
func isBlockedRequest(err error) bool {
	if err == nil {
		return false
	}

	// Check safeurl typed errors - use errors.As for type checking
	var (
		ipv6Err              *safeurl.IPv6BlockedError
		portErr              *safeurl.AllowedPortError
		schemeErr            *safeurl.AllowedSchemeError
		invalidHostErr       *safeurl.InvalidHostError
		ipErr                *safeurl.AllowedIPError
		redirectsDisabledErr *redirectsDisabledError
	)

	return errors.As(err, &ipv6Err) ||
		errors.As(err, &portErr) ||
		errors.As(err, &schemeErr) ||
		errors.As(err, &invalidHostErr) ||
		errors.As(err, &ipErr) ||
		errors.As(err, &redirectsDisabledErr)
}
```

**File:** core/services/workflows/syncer/v2/fetcher.go (L184-196)
```go
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

**File:** core/services/workflows/artifacts/v2/store.go (L143-183)
```go
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

**File:** core/services/cre/cre.go (L807-845)
```go
func newFetcherServiceV2(
	opts Opts,
	capCfg config.Capabilities,
	lggr logger.Logger,
	gatewayConnectorWrapper *gatewayconnector.ServiceWrapper,
) (wftypes.FetcherFunc, wftypes.LocationRetrieverFunc, []commonsrv.Service, error) {
	if opts.FetcherFunc != nil {
		return opts.FetcherFunc, nil, []commonsrv.Service{}, nil
	}

	if gatewayConnectorWrapper == nil {
		return nil, nil, nil, errors.New("unable to create workflow registry syncer without gateway connector")
	}

	wfStorage := capCfg.WorkflowRegistry().WorkflowStorage()
	storageClient := opts.StorageClient
	if wfStorage.URL() != "" {
		workflowOpts := []storage.WorkflowClientOpt{
			storage.WithJWTGenerator(opts.JWTGenerator),
		}
		if wfStorage.TLSEnabled() {
			workflowOpts = append(workflowOpts, storage.WithWorkflowTransportCredentials(credentials.NewClientTLSFromCert(nil, "")))
		}

		sc, err := storage.NewWorkflowClient(lggr, wfStorage.URL(), workflowOpts...)
		if err != nil {
			return nil, nil, nil, fmt.Errorf("failed to create storage client: %w", err)
		}

		storageClient = sc
	}

	if storageClient == nil {
		return nil, nil, nil, errors.New("must have a storage client")
	}

	fetcher := syncerV2.NewFetcherService(lggr, gatewayConnectorWrapper, storageClient)
	return fetcher.Fetch, fetcher.RetrieveURL, []commonsrv.Service{fetcher}, nil
}
```
