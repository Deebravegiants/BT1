## Analysis

The report describes a classic path-traversal vulnerability in a static file server (`serve` module): an unvalidated path segment (`../../../../etc/passwd`) escapes the intended serving root. Searching the chainlink codebase for an analogous unprivileged-reachable path-handling bug in file-fetching / gateway code turns up two comparable "base path containment" implementations in `core/services/workflows/syncer/v2/fetcher.go`, used by the workflow artifact `Store` to fetch workflow binaries/configs whose URLs (`BinaryURL`/`ConfigURL`) originate from workflow registration data (attacker/workflow-owner controlled), as seen in `core/services/workflows/artifacts/v2/store.go` (`FetchWorkflowArtifacts`).

The `newFileFetcher` implementation correctly guards against traversal: it cleans the path and then explicitly verifies `strings.HasPrefix(fullPath, basePath+string(filepath.Separator))` before reading, which is confirmed correct by the traversal test case in `fetcher_test.go`. [1](#0-0) 

However, `newHTTPFetcher` — used for `http`/`https` base URLs (the artifact-storage / gateway path) — only does a superficial clean-and-trim, then joins with the base path using `filepath.Join`, **without ever verifying the resulting path is still contained within the original base path**: [2](#0-1) 

Because `filepath.Join` itself calls `Clean`, a `req.URL` containing enough `../` segments (e.g. `../../other-tenant/binary.wasm`) will resolve `u.Path` to a location *outside* the intended base path prefix on the same host, with no containment check comparable to the one in `newFileFetcher`. This is different from the file-fetcher, which explicitly re-validates containment after joining/cleaning.

### Where attacker-controlled input enters
`BinaryURL`/`ConfigURL` supplied at workflow registration time (by any workflow owner — an unprivileged/permissionless actor in a CRE-style DON deployment) flow directly into `ghcapabilities.Request.URL` and then into `fetchFn`, which resolves to `newHTTPFetcher` when the base URL scheme is `http`/`https`: [3](#0-2) [4](#0-3) 

The comment `// Clean the path to prevent directory traversal` at line 249 in `fetcher.go` documents the intended mitigation, but the code does not actually verify the final joined path stays under the intended prefix.

### Title
Path Traversal in Workflow Artifact HTTP Fetcher Allows Escaping Intended Base Path - (File: core/services/workflows/syncer/v2/fetcher.go)

### Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds a fetch URL by joining a fixed `baseURL` path with a workflow-supplied `req.URL`. It attempts to sanitize the path with `filepath.Clean`/`TrimPrefix`, but never re-checks that the final resolved path (after `filepath.Join`, which itself performs `Clean` and can collapse `../` sequences across the base) remains within the original base path, unlike the equivalent `newFileFetcher` implementation which explicitly enforces containment.

### Finding Description
`req.URL` for artifact fetches originates from workflow-registration data (`BinaryURL`/`ConfigURL`), which is effectively caller/workflow-owner controlled, as passed through `Store.FetchWorkflowArtifacts` into `ghcapabilities.Request{URL: binaryURL/configURL, ...}` and then to `h.fetchFn`. When the configured artifact source uses `http`/`https`, `NewFetcherFunc` returns `newHTTPFetcher`, whose path handling is:
```go
cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")
...
u.Path = filepath.Join(u.Path, cleanPath)
```
`filepath.Join` normalizes `..` segments relative to the joined result, not relative only to `cleanPath`, so a value like `../../secret/path` (or an absolute-looking value that reduces to enough `..` segments) can walk `u.Path` outside the intended base directory on the artifact host. There is no subsequent check (as exists in `newFileFetcher` via `strings.HasPrefix(fullPath, basePath+separator)`) confirming the final `u.Path` still starts with the original base path.

### Impact Explanation
This can let an unprivileged workflow owner cause the chainlink node/gateway to fetch resources outside the intended artifact-storage prefix on the same artifact-storage host — potentially retrieving other tenants'/workflows' binaries or configuration data, or any other resource reachable at that host/path outside the sanctioned directory, resulting in cross-user data disclosure via the node's outbound fetch capability.

### Likelihood Explanation
Reaching this path only requires registering (or updating) a workflow with a crafted `BinaryURL`/`ConfigURL` containing traversal sequences — an action available to any workflow owner in a permissionless/DON deployment, with no additional authentication bypass needed. The fetch is automatically triggered by `FetchWorkflowArtifacts` during normal workflow sync.

### Recommendation
In `newHTTPFetcher`, after computing `u.Path = filepath.Join(u.Path, cleanPath)`, verify the resulting path still has the original base path as a prefix (mirroring the check already present in `newFileFetcher`), and reject the request otherwise.

### Proof of Concept
1. Configure an HTTP-based artifact `baseURL`, e.g. `https://storage.example.com/tenants/tenantA/`.
2. Register/update a workflow whose `BinaryURL` (or `ConfigURL`) is set to a value that, once `filepath.Clean`+`filepath.Join`-ed with the base path, escapes the `tenants/tenantA/` prefix, e.g. supplying `req.URL = "../tenantB/binary.wasm"`.
3. `Store.FetchWorkflowArtifacts` invokes `fetchFn` → `newHTTPFetcher`, which builds `fetchURL = https://storage.example.com/tenants/tenantB/binary.wasm` and fetches it — returning tenant B's artifact to tenant A's workflow — with no containment check to prevent this. [2](#0-1)

### Citations

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

**File:** core/services/workflows/artifacts/v2/store.go (L174-182)
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
```

**File:** core/services/workflows/artifacts/v2/store.go (L217-227)
```go
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
