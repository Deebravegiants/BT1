This is a legitimate finding, so I'll do a proper security write-up rather than a vulnerability disclaimer.

### Title
Path-Traversal in CRE `newHTTPFetcher` allows attacker-supplied Workflow BinaryURL/ConfigURL to escape the configured fetch path prefix - (File: `core/services/workflows/syncer/v2/fetcher.go`)

### Summary
When a Chainlink node is configured with `CRE.WorkflowFetcher.URL` pointing to an `http(s)://` endpoint, artifact fetching bypasses the gateway and uses `newHTTPFetcher`, which builds the outbound request path by joining the configured base path with an attacker-controlled `req.URL` without verifying the result stays inside the base path [1](#0-0) . This is the same bug class as CVE-2023-4760: a path-containment check is missing/insufficient after path normalization, letting a caller-controlled value break out of an intended base directory/prefix.

### Finding Description
`NewFetcherFunc` builds a `FetcherFunc` from the operator-configured `CRE.WorkflowFetcher.URL`. For `http`/`https` schemes it returns `newHTTPFetcher`, which is invoked per-artifact-fetch with `req.URL` [2](#0-1) :

```go
cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")
u, err := url.Parse(baseURL)
...
u.Path = filepath.Join(u.Path, cleanPath)
fetchURL := u.String()
``` [1](#0-0) 

`filepath.Join` itself calls `filepath.Clean` on the combined path, resolving any `../` segments. If `req.URL` contains enough `../` sequences, the resulting `u.Path` can escape the base path entirely (e.g. base path `/workflows` + `req.URL = "../../internal/secret"` → `u.Path = "/internal/secret"`). Unlike the sibling `newFileFetcher`, which explicitly re-validates that the resolved path is still prefixed by `basePath+separator` before use [3](#0-2) , `newHTTPFetcher` performs no equivalent containment check after `filepath.Join`.

`req.URL` here is not operator input — it is the `BinaryURL`/`ConfigURL` taken directly from an on-chain `WorkflowRegisteredEvent`, i.e., supplied by whoever registers a workflow on the Workflow Registry contract. This flows through `createWorkflowSpec` → `FetchWorkflowArtifacts` → `h.fetchFn(...)` unmodified [4](#0-3) [5](#0-4) , meaning an unprivileged workflow author fully controls the string that becomes `req.URL`.

### Impact Explanation
On a node configured with an `http(s)://` `CRE.WorkflowFetcher.URL` (a documented, supported configuration bypassing the gateway) [6](#0-5) , a workflow author can force the node to issue outbound HTTP GET requests to arbitrary paths on the configured fetcher host rather than the intended artifact path prefix. This can be used to reach internal endpoints reachable only via that host/path-routing (e.g., internal admin or metadata paths behind the same reverse proxy), resulting in unauthorized disclosure of whatever that alternate path serves, and the response is fed back into the workflow artifact pipeline (decoded as base64 binary/config and stored) — i.e., request impersonation / SSRF against the configured artifact host.

### Likelihood Explanation
Requires the operator to have configured `CRE.WorkflowFetcher.URL` with `http`/`https` (not the `file://` scheme shown in the default sample configs) [7](#0-6) . Given that configuration, exploitation requires no special privilege beyond the ability to register a workflow (`BinaryURL`/`ConfigURL` are attacker-supplied fields of the on-chain registration event), making it trivially reachable once the feature is enabled.

### Recommendation
Add the same containment check used in `newFileFetcher` to `newHTTPFetcher`: after computing `u.Path = filepath.Join(baseU.Path, cleanPath)`, verify it is still prefixed by the original base path (with separator boundary) before issuing the request, and reject otherwise.

### Proof of Concept
1. Configure `CRE.WorkflowFetcher.URL = "http://internal-host/workflows"`.
2. Register a workflow on-chain with `BinaryURL = "http://internal-host/workflows/../../admin/secret"` (or any value that, once `filepath.Clean`+`filepath.Join`-normalized, resolves outside `/workflows`).
3. The node's `newHTTPFetcher` builds `fetchURL = "http://internal-host/admin/secret"` and fetches it, returning the response content into the workflow artifact pipeline instead of enforcing the `/workflows` prefix. [1](#0-0) [8](#0-7) [9](#0-8)

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L198-231)
```go
func newFileFetcher(basePath string, lggr logger.Logger) types.FetcherFunc {
	return func(ctx context.Context, messageID string, req ghcapabilities.Request) ([]byte, error) {
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		default:
		}

		// the incoming request URL is expected to be a relative path or a path within the basePath
		if req.URL == "" {
			return nil, errors.New("request URL cannot be empty")
		}
		u, err := url.Parse(req.URL)
		if err != nil {
			return nil, fmt.Errorf("invalid URL: %w", err)
		}
		// Confidential workflows register with HTTP URLs (for the enclave).
		// Extract the filename so the file fetcher can find the local copy.
		if u.Scheme == "http" || u.Scheme == "https" {
			u.Path = filepath.Base(u.Path)
			if u.Path == "." || u.Path == "/" {
				return nil, errors.New("HTTP URL has no filename in path")
			}
		}
		fullPath := filepath.Clean(u.Path)

		// ensure that the incoming request URL is either relative or absolute but within the basePath
		if !filepath.IsAbs(fullPath) {
			// If it's not absolute, we assume it's relative to the basePath
			fullPath = filepath.Join(basePath, fullPath)
		}
		if !strings.HasPrefix(fullPath, basePath+string(filepath.Separator)) && fullPath != basePath {
			return nil, fmt.Errorf("request URL %s is not within the basePath %s", fullPath, basePath)
		}
```

**File:** core/services/workflows/syncer/v2/fetcher.go (L243-261)
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
```

**File:** core/services/workflows/artifacts/v2/store.go (L143-184)
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

**File:** core/services/workflows/syncer/v2/handler.go (L797-801)
```go
	// With Workflow Registry contract v2 the BinaryURL and ConfigURL are expected to be identifiers that put through the Storage Service.
	decodedBinary, config, err := h.workflowArtifactsStore.FetchWorkflowArtifacts(ctx, wfID, payload.BinaryURL, payload.ConfigURL)
	if err != nil {
		return nil, err
	}
```

**File:** core/services/chainlink/config_cre_test.go (L93-100)
```go
		{
			name: "HTTP URL",
			config: `
[CRE.WorkflowFetcher]
URL = "http://example.com/workflows"
`,
			expected: "http://example.com/workflows",
		},
```

**File:** core/scripts/cre/environment/configs/mixed-env-confidential-workflows.toml.tmpl (L126-128)
```text
      [CRE.WorkflowFetcher]
      URL = "file:///home/chainlink/workflows"
      """
```
