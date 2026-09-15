### Title
Missing path-containment check in `newHTTPFetcher` allows workflow-owner-controlled URL to escape the configured base path - (File: `core/services/workflows/syncer/v2/fetcher.go`)

### Summary
`core/services/workflows/syncer/v2/fetcher.go` implements two `FetcherFunc` variants used to download workflow binary/config artifacts by URL: `newFileFetcher` and `newHTTPFetcher`. `newFileFetcher` correctly enforces that the resolved path stays within `basePath` via a separator-safe prefix check [1](#0-0) . `newHTTPFetcher`, however, only cleans the request path and joins it onto the base URL without ever verifying that the resulting path remains under the intended base path segment [2](#0-1) . This mirrors the Gradio `is_in_or_equal` bug class: a containment check that exists for one path but is absent/bypassable for another, allowing `..` sequences to escape the intended directory scope.

### Finding Description
`req.URL` in `newHTTPFetcher` is fully attacker-influenced: it originates from `binaryURL`/`configURL` values supplied when a workflow is registered, which are passed straight into `ghcapabilities.Request{URL: binaryURL, ...}` / `{URL: configURL, ...}` in `Store.FetchWorkflowArtifacts` [3](#0-2) [4](#0-3) . These URLs are attacker(workflow author/owner)-controlled and are only redirected through the artifact-storage signed-URL path when their host matches `ArtifactStorageHost`; otherwise the raw, unprivileged-supplied URL is fetched directly [5](#0-4) .

In `newHTTPFetcher`, the code cleans the path with `filepath.Clean` and trims a leading `/`, then joins it onto the configured base URL's path with `filepath.Join`, which itself resolves any remaining `..` components:
```go
cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")
...
u.Path = filepath.Join(u.Path, cleanPath)
``` [2](#0-1) 
Because `filepath.Join` also calls `Clean` on the combined result, a `req.URL` value containing enough `../` segments (e.g. `../../secret-bucket/file`) collapses past the intended sub-path segment configured in `baseURL`, producing a request path outside of what the deployment operator intended to expose — with no subsequent prefix/containment check comparable to the one in `newFileFetcher`. This is the same root-cause class as the Gradio advisory: a containment/allowlist check exists conceptually ("Clean the path to prevent directory traversal") but is not actually a containment check — it merely normalizes the path without verifying it stays under the base.

### Impact Explanation
Since only the URL path is manipulated (the host taken from the configured `baseURL` cannot be changed by the attacker), this is not full SSRF to arbitrary hosts, but it is a scope/allowlist bypass: a workflow owner can cause the Chainlink node to fetch content from arbitrary paths on the host configured for artifact fetching, beyond the sub-path the operator intended to restrict fetching to (e.g., escaping a designated `/artifacts/<org>/` prefix to reach other tenants' or internal paths on the same host). This is a Medium-severity allowlist-bypass analogous to the Gradio finding, reachable from an unprivileged workflow-registration actor.

### Likelihood Explanation
Likelihood is moderate: it requires (1) an operator to configure the CRE/workflow fetcher with an `http`/`https` base URL that assumes a sub-path restriction, and (2) a workflow owner able to register a workflow with a crafted `binaryURL`/`configURL` containing `../` sequences that doesn't match `ArtifactStorageHost` (so it bypasses the signed-URL redirection and goes straight to `newHTTPFetcher`). No special privileges beyond normal workflow registration are needed.

### Recommendation
Add the same containment check used in `newFileFetcher` to `newHTTPFetcher`: after joining, verify the resulting `u.Path` still has the original base path as a prefix (with a separator boundary), and reject the request otherwise, rather than relying solely on `filepath.Clean`/`filepath.Join` normalization.

### Proof of Concept
1. Operator configures workflow artifact fetching with `baseURL = "https://artifacts.example.com/org-a/workflows/"`, intending all fetches to be scoped under `/org-a/workflows/`.
2. A workflow owner registers a workflow with `binaryURL` (or `configURL`) whose host differs from `ArtifactStorageHost` (or matches `baseURL`'s host but is not proxied via the signed-URL retrieval path), set to a request URL such as `"../../org-b/secrets/config.json"`.
3. `Store.FetchWorkflowArtifacts` builds `ghcapabilities.Request{URL: "../../org-b/secrets/config.json", ...}` and calls `fetchFn` [3](#0-2) .
4. `newHTTPFetcher` computes `cleanPath = "../../org-b/secrets/config.json"`, then `u.Path = filepath.Join("/org-a/workflows/", cleanPath)`, which resolves to `/org-b/secrets/config.json` — outside the intended `/org-a/workflows/` scope — and issues the HTTP GET with no containment check [6](#0-5) .

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L248-267)
```go
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

**File:** core/services/workflows/artifacts/v2/store.go (L149-161)
```go
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
```

**File:** core/services/workflows/artifacts/v2/store.go (L174-180)
```go
	req := ghcapabilities.Request{
		URL:              binaryURL,
		Method:           http.MethodGet,
		MaxResponseBytes: safeUint32(uint64(maxBinarySize)),
		WorkflowID:       workflowID,
	}
	binary, err = h.fetchFn(ctx, messageID(binaryURL, workflowID), req)
```

**File:** core/services/workflows/artifacts/v2/store.go (L217-224)
```go
		req := ghcapabilities.Request{
			URL:              configURL,
			Method:           http.MethodGet,
			MaxResponseBytes: safeUint32(uint64(maxResponseBytes)),
			WorkflowID:       workflowID,
		}

		config, err2 = h.fetchFn(ctx, messageID(configURL, workflowID), req)
```
