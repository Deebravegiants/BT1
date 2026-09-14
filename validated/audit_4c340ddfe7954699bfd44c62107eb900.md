### Title
Directory Traversal in Workflow HTTP Artifact Fetcher via Unsanitized `binaryURL`/`configURL` - (File: `core/services/workflows/syncer/v2/fetcher.go`)

### Summary
The `newHTTPFetcher` closure in `core/services/workflows/syncer/v2/fetcher.go` fetches workflow binary/config artifacts from an operator-configured base HTTP URL, joined with an attacker-influenced request path. The path-traversal guard it uses is insufficient: `filepath.Join` re-normalizes `..` segments against the configured base path, allowing the effective request path to escape the intended artifact root, unlike the sibling `newFileFetcher` in the same file, which explicitly validates the resolved path stays within `basePath` via a `strings.HasPrefix` check.

### Finding Description
`NewFetcherFunc` builds either a file-based or HTTP-based fetcher depending on the `CRE.WorkflowFetcher.URL` scheme configured by the operator [1](#0-0) .

For the HTTP case, `newHTTPFetcher` attempts to sanitize the incoming `req.URL` before appending it to the configured base path:
```go
cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")
...
u.Path = filepath.Join(u.Path, cleanPath)
``` [2](#0-1) 

`filepath.Clean` alone does not eliminate leading `..` sequences that have no preceding path component to cancel against (e.g. `../../../etc/passwd` remains unchanged). The subsequent `filepath.Join(u.Path, cleanPath)` then normalizes the full combined path, which *can* walk `..` segments upward past the operator-configured base path (`u.Path`), effectively escaping the intended artifact root — there is no post-join containment check like the one performed in `newFileFetcher`:
```go
if !strings.HasPrefix(fullPath, basePath+string(filepath.Separator)) && fullPath != basePath {
    return nil, fmt.Errorf("request URL %s is not within the basePath %s", fullPath, basePath)
}
``` [3](#0-2) 

The `req.URL` value fed into this fetcher originates from `binaryURL`/`configURL`, which are populated directly from the on-chain `WorkflowRegisteredEvent.BinaryURL` / `ConfigURL` fields supplied by whoever registers the workflow — an unprivileged workflow owner, not a privileged operator:
```go
req := ghcapabilities.Request{
    URL: binaryURL, ...
}
binary, err = h.fetchFn(ctx, messageID(binaryURL, workflowID), req)
``` [4](#0-3) 

The HTTP fetcher is wired in when `CRE.WorkflowFetcher.URL` is an `http://`/`https://` URL, which is a supported and documented deployment configuration (`docs/CONFIG.md` / `config_cre_test.go`) [5](#0-4) . Any operator running this fetcher against an internal HTTP artifact host with a non-root path prefix (e.g., `https://internal-artifacts/workflows`) is exposed: a workflow owner controls `binaryURL`/`configURL` and can supply a value that, once joined and re-normalized, resolves outside the `/workflows` prefix on that internal host.

### Impact Explanation
An unprivileged workflow owner who can register a workflow on-chain (setting arbitrary `BinaryURL`/`ConfigURL` strings) can cause the node's fetcher to request unintended paths on the operator's internal HTTP artifact host, bypassing the intended path confinement ("allowlist") that scopes fetches to the configured workflow artifact directory. This is directly analogous to the ProjectSend directory-traversal bug class (unsanitized path parameter escaping the intended storage root), applied here to the internet/internal-facing workflow artifact retrieval path instead of a PHP upload directory.

### Likelihood Explanation
Exploitability depends on the operator's deployment using the HTTP variant of `CRE.WorkflowFetcher.URL` with a non-root path component (the documented file-based CRE test/dev configs use `file:///home/chainlink/workflows`, which uses the correctly-guarded `newFileFetcher` path instead). Where the HTTP variant with a path prefix is used, any address able to register a workflow can trigger the traversal purely through the on-chain `BinaryURL`/`ConfigURL` fields, requiring no special privilege beyond normal workflow registration.

### Recommendation
Apply the same containment check used in `newFileFetcher` to `newHTTPFetcher`: after computing `fetchURL`/`u.Path`, verify the resolved path retains the configured base path as a strict prefix, and reject the request otherwise, rather than relying on `filepath.Clean` + `filepath.Join` alone.

### Proof of Concept
1. Operator configures `[CRE.WorkflowFetcher] URL = "https://internal-artifacts.example/workflows"`.
2. An unprivileged actor registers a workflow on-chain with `ConfigURL` (or `BinaryURL`) set to a value such as `../../secrets/other-tenant-config.yaml`.
3. `FetchWorkflowArtifacts` passes this value as `req.URL` into the configured `fetchFn`, which resolves to `newHTTPFetcher` [6](#0-5) .
4. Inside `newHTTPFetcher`, `filepath.Join("/workflows", "../../secrets/other-tenant-config.yaml")` normalizes to a path outside `/workflows` on `internal-artifacts.example`, and the request is issued without any prefix-containment check [7](#0-6) , returning the fetched (unintended) content to the requesting workflow's artifact pipeline.

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L222-231)
```go
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

**File:** core/services/workflows/syncer/v2/fetcher.go (L243-266)
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
```

**File:** core/services/workflows/artifacts/v2/store.go (L174-183)
```go
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

**File:** core/services/workflows/artifacts/v2/store.go (L216-227)
```go
		// Fetch the config files from the specified URLs.
		req := ghcapabilities.Request{
			URL:              configURL,
			Method:           http.MethodGet,
			MaxResponseBytes: safeUint32(uint64(maxResponseBytes)),
			WorkflowID:       workflowID,
		}

		config, err2 = h.fetchFn(ctx, messageID(configURL, workflowID), req)
		if err2 != nil {
			return nil, nil, &types.ArtifactFetchError{ArtifactType: "config", URL: configURL, Err: err2}
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
