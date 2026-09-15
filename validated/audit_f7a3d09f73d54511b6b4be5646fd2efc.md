Audit Report

## Title
Path Traversal in Workflow Artifact HTTP Fetcher Allows Escaping Intended Base Path - (File: core/services/workflows/syncer/v2/fetcher.go)

## Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds the artifact-fetch URL by joining a fixed `baseURL` path with a workflow-supplied `req.URL` using `filepath.Join`, but never re-validates that the resulting path remains within the original base path prefix. This is inconsistent with the sibling `newFileFetcher` implementation, which explicitly performs that containment check, confirming the omission in the HTTP path is a genuine gap rather than intentional design.

## Finding Description
`newHTTPFetcher` computes:
```go
cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")
...
u.Path = filepath.Join(u.Path, cleanPath)
``` [1](#0-0) 

`filepath.Join` internally calls `Clean` on the combined result, so leading `../` segments in `cleanPath` are resolved relative to `u.Path`, not blocked. For example, with `baseURL = "https://storage.example.com/tenants/tenantA"` and `req.URL = "../tenantB/binary.wasm"`, the resulting `u.Path` becomes `/tenants/tenantB/binary.wasm` — escaping the intended tenant-scoped prefix on the same host. There is no subsequent prefix check comparable to the one enforced in `newFileFetcher`:
```go
if !strings.HasPrefix(fullPath, basePath+string(filepath.Separator)) && fullPath != basePath {
    return nil, fmt.Errorf("request URL %s is not within the basePath %s", fullPath, basePath)
}
``` [2](#0-1) 

This asymmetry is corroborated by the test suite: `fetcher_test.go` includes an explicit path-traversal test for the file fetcher (`"is not within the basePath"`) but has no equivalent traversal test for the HTTP fetcher, only positive-path and 404 cases. [3](#0-2) [4](#0-3) 

`req.URL` for artifact fetches is populated from `BinaryURL`/`ConfigURL` in `Store.FetchWorkflowArtifacts`, which are supplied at workflow-registration time and are effectively workflow-owner controlled: [5](#0-4) [6](#0-5) 

`NewFetcherFunc` dispatches to `newHTTPFetcher` whenever the configured artifact base URL scheme is `http`/`https`: [7](#0-6) 

I was unable to conclusively verify, within the available tooling, which of the two fetch mechanisms (`FetcherService.Fetch`, which routes through the gateway, versus the direct `NewFetcherFunc`-produced `newHTTPFetcher`/`newFileFetcher`, which the code comment explicitly says "bypasses the gateway") is actually wired into `Store.fetchFn` in a typical production node deployment. `NewFetcherFunc` is only referenced from `core/cmd/shell.go` in this codebase (besides tests), suggesting it may be configured for specific (e.g., local/dev or confidential-compute) deployment modes rather than the default gateway-mediated production path. This affects likelihood but not the validity of the underlying code defect.

## Impact Explanation
When the artifact-storage fetcher is configured with an `http`/`https` base URL, an attacker-controlled `BinaryURL`/`ConfigURL` containing `../` sequences can cause the node to fetch resources outside the intended base-path prefix on the same artifact-storage host, e.g., retrieving another tenant's/workflow's binary or configuration data. This maps to a cross-user data disclosure impact via the node's outbound artifact-fetch capability, in the same class as the already-mitigated file-fetcher traversal.

## Likelihood Explanation
Exploitation only requires an unprivileged workflow owner to register/update a workflow with a crafted `BinaryURL`/`ConfigURL`; `FetchWorkflowArtifacts` triggers the fetch automatically during normal workflow sync, with no additional privilege needed on the attacker's part. Likelihood in a given deployment depends on whether that deployment's `Store.fetchFn` is actually wired to the `NewFetcherFunc`/`newHTTPFetcher` path (bypass mode) versus the gateway-mediated `FetcherService.Fetch` path, which I could not fully confirm.

## Recommendation
In `newHTTPFetcher`, after computing `u.Path = filepath.Join(u.Path, cleanPath)`, verify the resulting path still has the original base path as a prefix (mirroring the check in `newFileFetcher`), and reject the request if it does not.

## Proof of Concept
1. Configure `NewFetcherFunc` with an HTTP base URL, e.g. `https://storage.example.com/tenants/tenantA/`.
2. Call the resulting `FetcherFunc` with `ghcapabilities.Request{URL: "../tenantB/binary.wasm"}`.
3. Observe that `newHTTPFetcher` builds `fetchURL = https://storage.example.com/tenants/tenantB/binary.wasm` and issues the request, with no error raised for escaping the `tenants/tenantA/` prefix — unlike the equivalent traversal attempt against `newFileFetcher`, which is rejected with `"is not within the basePath"`.
4. A Go unit test analogous to the existing `"file fetcher"` traversal test in `fetcher_test.go`, but targeting `"http fetcher"` with a traversal `req.URL`, would demonstrate the missing containment check.

### Citations

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L248-258)
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

**File:** core/services/workflows/syncer/v2/fetcher_test.go (L500-532)
```go
	t.Run("http fetcher", func(t *testing.T) {
		t.Parallel()
		// Create test HTTP server
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.URL.Path == "/workflows/test.json" {
				w.WriteHeader(http.StatusOK)
				_, err := w.Write(testContent)
				assert.NoError(t, err)
			} else {
				w.WriteHeader(http.StatusNotFound)
			}
		}))
		defer server.Close()

		baseURL := server.URL + "/workflows"
		fetcher, err := NewFetcherFunc(baseURL, lggr)
		require.NoError(t, err)
		require.NotNil(t, fetcher)

		// Test fetching valid URL
		resp, err := fetcher(ctx, "test-msg-id", ghcapabilities.Request{
			URL: "test.json",
		})
		require.NoError(t, err)
		assert.Equal(t, testContent, resp)

		// Test fetching non-existent resource
		_, err = fetcher(ctx, "test-msg-id", ghcapabilities.Request{
			URL: "nonexistent.json",
		})
		require.Error(t, err)
		assert.Contains(t, err.Error(), "HTTP request failed with status code: 404")
	})
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
