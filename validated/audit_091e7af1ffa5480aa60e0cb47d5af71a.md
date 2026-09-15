The workflow registration flow is permissionless at the workflow-owner level; any registered workflow supplies `BinaryURL`/`ConfigURL` values that flow unmodified into the fetcher's `req.URL`. I've confirmed the code behaves exactly as described.

Audit Report

## Title
Path traversal in workflow artifact HTTP fetcher allows escaping configured base URL - (File: core/services/workflows/syncer/v2/fetcher.go)

## Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds the outbound artifact-fetch URL by joining the operator-configured base path with an attacker/workflow-owner-controlled `req.URL` using `filepath.Clean` + `filepath.Join`, without verifying the resolved path stays under the configured base path. [1](#0-0)  This is unlike its `file://` sibling `newFileFetcher`, which explicitly checks the resolved path retains the `basePath` prefix and rejects traversal. [2](#0-1) 

## Finding Description
`filepath.Clean(req.URL)` does not strip leading `..` segments from a relative path; it only normalizes them. `filepath.Join(u.Path, cleanPath)` then resolves those `..` segments against the base path via its own internal `Clean`, so a `req.URL` such as `../../etc/passwd` collapses `/workflows/../../etc/passwd` down to `/etc/passwd` — escaping the configured base path entirely. [3](#0-2)  No post-join prefix check exists afterward, unlike `newFileFetcher`'s `strings.HasPrefix(fullPath, basePath+string(filepath.Separator))` guard. [4](#0-3) 

The unit test for the HTTP variant confirms the base URL + relative-filename join pattern is the intended, supported usage (`baseURL := server.URL + "/workflows"`, `req.URL: "test.json"`), but there is no equivalent traversal-rejection test for the HTTP fetcher, unlike the explicit `../../../etc/passwd` rejection test that exists only for the file fetcher. [5](#0-4) [6](#0-5) 

`req.URL` originates from `BinaryURL`/`ConfigURL`, which are passed straight into `ghcapabilities.Request{URL: binaryURL, ...}` and into `h.fetchFn` (the `FetcherFunc` produced by `NewFetcherFunc`) inside `Store.FetchWorkflowArtifacts`. [7](#0-6)  These fields are supplied by whoever registers the workflow, and `WorkflowFetcherConfig.URL` is validated to explicitly permit `http`/`https` schemes as an operator-supported override for the fetcher. [8](#0-7) 

## Impact Explanation
If an operator configures `CRE.WorkflowFetcher.URL` with `http`/`https` scheme pointing at an artifact host serving other content under the same origin, a workflow owner can supply a crafted `BinaryURL`/`ConfigURL` to make the node fetch arbitrary paths on that host outside the intended artifact directory — an information-disclosure/SSRF-style path traversal confined to the configured artifact host. The `file://` scheme is unaffected because `newFileFetcher` implements the correct prefix check. [9](#0-8) 

## Likelihood Explanation
This requires the operator to opt into `http`/`https` scheme for `CRE.WorkflowFetcher.URL` (a documented, valid configuration per `ValidateConfig`), combined with a node accepting workflow registrations whose `BinaryURL`/`ConfigURL` fields are attacker-influenced. [10](#0-9)  Given that `NewFetcherFunc` explicitly supports and documents bypassing the gateway for both `file` and `http(s)` schemes with the same conceptual base-path model, this is a realistic, supported deployment path rather than a contrived edge case. [11](#0-10) 

## Recommendation
In `newHTTPFetcher`, after computing `u.Path = filepath.Join(u.Path, cleanPath)`, verify the resulting path retains the original base path as a prefix, mirroring the check already present in `newFileFetcher` at lines 229-231, and/or reject any `req.URL` containing `..` segments before joining.

## Proof of Concept
1. Start an `httptest.Server` and configure `baseURL := server.URL + "/workflows"`, then `fetcher, _ := NewFetcherFunc(baseURL, lggr)` (mirrors the existing `"http fetcher"` test setup). [12](#0-11) 
2. Call `fetcher(ctx, "test-msg-id", ghcapabilities.Request{URL: "../../etc/passwd"})`.
3. Observe the constructed `fetchURL` resolves outside `/workflows` (e.g., `.../etc/passwd`) and an HTTP GET is issued to that path, whereas the equivalent file-fetcher test explicitly rejects this input with "is not within the basePath". [6](#0-5) 
4. Add assertions confirming the request path sent to the test server differs from the configured `/workflows` prefix, proving the traversal.

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L248-259)
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
