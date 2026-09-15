### Title
Path traversal in workflow artifact HTTP fetcher allows escaping configured base URL - (File: core/services/workflows/syncer/v2/fetcher.go)

### Summary
`WorkflowFetcherConfig.URL` (`CRE.WorkflowFetcher.URL`) is an optional, operator-configured base URL that backs `NewFetcherFunc`, which produces the `FetcherFunc` used to download workflow binary/config artifacts referenced by `BinaryURL`/`ConfigURL` on `WorkflowRegisteredEvent`. [1](#0-0)  When the base URL scheme is `http`/`https`, `newHTTPFetcher` builds the outbound request path by joining the base path with the attacker/workflow-owner supplied `req.URL` without adequately preventing traversal beyond the base path, unlike its `file://` sibling `newFileFetcher`, which does correctly enforce a "must remain under basePath" prefix check (and has a passing test asserting rejection of `../../../etc/passwd`). [2](#0-1) 

### Finding Description
`newHTTPFetcher` computes the fetch path like this:
```go
cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")
...
u.Path = filepath.Join(u.Path, cleanPath)
fetchURL := u.String()
``` [3](#0-2) 

`filepath.Clean` does not remove leading `..` segments from a relative path (it only collapses/simplifies them), and `filepath.Join` subsequently resolves those `..` segments against the base path (`u.Path`) via its own `Clean` call. As a result, a `req.URL` value such as `../../etc/passwd` (or any value with enough leading `..` segments) can cause `filepath.Join(basePath, cleanPath)` to resolve *outside* the operator-configured base directory/prefix on the target HTTP host — e.g. joining `/workflows` with `../../etc/passwd` yields `/etc/passwd` — and the resulting `fetchURL` is fetched via a plain outbound HTTP GET with no post-join verification that the final path is still within `u.Path`'s original prefix. [4](#0-3) 

This is exactly the same root-cause pattern as ALPINE-CVE-2021-29133 (`haserl` failing to verify a supplied path before serving file contents): the comment ("Clean the path to prevent directory traversal") documents an intended traversal guard, but the implementation neither strips `..` components nor validates the final resolved path stays within the configured prefix — only `newFileFetcher`'s local-disk variant has that check.

The `req.URL` value ultimately originates from `BinaryURL`/`ConfigURL` fields supplied at workflow registration time and flows unmodified into `ghcapabilities.Request.URL` → `Store.FetchWorkflowArtifacts` → `FetcherFunc` (`h.fetchFn`). [5](#0-4) [6](#0-5)  A workflow owner registering a workflow (an ordinary, unprivileged CRE/workflow-registry actor, not an operator or node peer) controls these URL fields.

### Impact Explanation
If a node operator configures `CRE.WorkflowFetcher.URL` with an `http(s)://` scheme pointing at an internal artifact host that also serves other content under the same origin (a common deployment pattern, mirroring the `file://` variant's intended "serve artifacts from a directory" model), a malicious or compromised workflow owner can supply a crafted `BinaryURL`/`ConfigURL` to make the node fetch arbitrary paths on that host — potentially retrieving unintended internal resources on the artifact server (information disclosure / SSRF-style pivot within the configured host), which is then decoded and treated as workflow binary/config content. This does not read local files (unlike `newFileFetcher`, which is properly guarded), so the impact is confined to path traversal against the configured HTTP artifact host rather than the node's local filesystem.

### Likelihood Explanation
Likelihood is moderate and conditional on deployment: it requires the operator to configure `CRE.WorkflowFetcher.URL` with an `http`/`https` scheme (the `file://` scheme is properly protected) and to run a workflow-registry-integrated node that accepts workflow registration from external/unprivileged owners. Given that `WorkflowFetcherConfig.URL` explicitly allows `http`/`https`/`file` schemes and is documented as an override for the fetcher service, this is a supported/expected configuration, not an edge case. [7](#0-6) 

### Recommendation
In `newHTTPFetcher`, after computing `u.Path = filepath.Join(u.Path, cleanPath)`, verify that the resulting path still has the original base path as a prefix (the same check already implemented in `newFileFetcher` at lines 229-231), and/or reject any `req.URL` containing `..` path segments outright before joining, rather than relying solely on `filepath.Clean`/`filepath.Join`'s traversal-agnostic normalization.

### Proof of Concept
1. Operator configures `CRE.WorkflowFetcher.URL = "https://artifacts.internal.example.com/workflows"`.
2. An unprivileged workflow owner registers a workflow with `BinaryURL = "../../../secret/other-tenant-config.json"`.
3. `Store.FetchWorkflowArtifacts` calls `h.fetchFn` with `ghcapabilities.Request{URL: "../../../secret/other-tenant-config.json", ...}`. [8](#0-7) 
4. `newHTTPFetcher` computes `cleanPath = "../../../secret/other-tenant-config.json"`, then `u.Path = filepath.Join("/workflows", cleanPath)`, resolving outside `/workflows` on `artifacts.internal.example.com`, and issues an HTTP GET there. [9](#0-8) 
5. Compare to the `file://` case, where the equivalent traversal attempt is explicitly tested and rejected: [10](#0-9)

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L198-241)
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

		lggr.Debugw("Fetching file", "messageID", messageID, "path", fullPath, "workflowID", req.WorkflowID)

		data, err := os.ReadFile(fullPath)
		if err != nil {
			return nil, fmt.Errorf("failed to read file: %w", err)
		}
		return data, nil
	}
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

**File:** core/services/workflows/artifacts/v2/store.go (L163-183)
```go
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

**File:** core/config/toml/types.go (L2135-2150)
```go
func (w *WorkflowFetcherConfig) ValidateConfig() error {
	if w.URL == nil || *w.URL == "" {
		return nil // URL is optional
	}

	u, err := url.Parse(*w.URL)
	if err != nil {
		return configutils.ErrInvalid{Name: "URL", Value: *w.URL, Msg: "must be a valid URL"}
	}

	if u.Scheme != "file" && u.Scheme != "http" && u.Scheme != "https" {
		return configutils.ErrInvalid{Name: "URL", Value: *w.URL, Msg: "scheme must be one of: file, http, https"}
	}

	return nil
}
```

**File:** core/services/workflows/syncer/v2/fetcher_test.go (L443-448)
```go
		// Test path traversal attempt
		_, err = fetcher(ctx, "test-msg-id", ghcapabilities.Request{
			URL: "../../../etc/passwd",
		})
		require.Error(t, err)
		assert.Contains(t, err.Error(), "is not within the basePath")
```
