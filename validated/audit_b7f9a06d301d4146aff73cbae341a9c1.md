Audit Report

## Title
Path Traversal in Workflow Artifact HTTP Fetcher Allows Escaping the Configured Base URL Prefix - (File: `core/services/workflows/syncer/v2/fetcher.go`)

## Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` joins the operator-configured `baseURL` with an externally-controlled `req.URL` using `filepath.Clean`/`filepath.Join`, but never verifies the joined result stays within the configured base path prefix, unlike its sibling `newFileFetcher`, which explicitly performs that check. [1](#0-0) [2](#0-1) 

## Finding Description
`NewFetcherFunc` selects `newHTTPFetcher` whenever `CRE.WorkflowFetcher.URL` is configured with an `http`/`https` scheme. [3](#0-2) 
`newHTTPFetcher`'s returned function computes `cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")` and then `u.Path = filepath.Join(u.Path, cleanPath)`, issuing an HTTP GET to the resulting URL, with no `strings.HasPrefix` check against the original base path — in contrast to `newFileFetcher`, which explicitly guards `fullPath` against escaping `basePath`. [4](#0-3) 
`filepath.Join` re-cleans the concatenated path, so a `req.URL` value containing sufficient `../` segments can make the final joined path escape the configured `u.Path` prefix. This mirrors the described root cause. `req.URL` originates from `binaryURL`/`configURL` used in `FetchWorkflowArtifacts`, which are sourced from workflow registration data. [5](#0-4) 
The gap is corroborated by the fact that the project's own tests exercise the traversal guard only for the file fetcher path, never for `newHTTPFetcher`.

## Impact Explanation
If a node operator configures `CRE.WorkflowFetcher.URL` with an HTTP(S) scheme (confirmed as a supported, documented configuration option — not merely theoretical), the resulting fetcher bypasses the gateway entirely and directly performs outbound HTTP requests based on workflow-supplied `URL` values. [6](#0-5) [7](#0-6) 
An entity able to register a workflow (setting `BinaryURL`/`ConfigURL`) could supply traversal sequences to redirect the request to unintended paths on the same host, potentially reaching internal endpoints not meant to be exposed to workflow owners. This falls into the "allowlist/prefix bypass leading to unauthorized backend access" impact class described.

## Likelihood Explanation
Exploitation requires the node operator to have explicitly opted into HTTP(S)-mode workflow fetching (bypassing the gateway) rather than the default gateway-based or `file://` fetch path — an explicit, non-default configuration choice that most production deployments using the gateway path would not hit. I was unable to fully verify within the available iterations (1) whether workflow registration on the Workflow Registry contract is truly permissionless/unprivileged for an arbitrary external actor, or (2) whether any onchain/offchain validation elsewhere sanitizes `BinaryURL`/`ConfigURL` before they reach `FetchWorkflowArtifacts`/`newHTTPFetcher`. However, based on the code reviewed, no such sanitization exists in the fetcher itself, and the described flow (workflow-registry-controlled URL → `FetchWorkflowArtifacts` → `newHTTPFetcher`) is consistent with the codebase structure found.

## Recommendation
Mirror the protection in `newFileFetcher`: after `u.Path = filepath.Join(u.Path, cleanPath)`, verify the resulting path is still prefixed by the original base path (`strings.HasPrefix`) and reject the request if not, or otherwise validate/reject `..` segments in `req.URL` before joining.

## Proof of Concept
1. Configure `CRE.WorkflowFetcher.URL = "http://internal-artifact-host/workflows"`.
2. Trigger `FetchWorkflowArtifacts` with a `ConfigURL`/`BinaryURL` such as `"../../admin/secrets"`.
3. Observe that `newHTTPFetcher` computes `fetchURL` as `http://internal-artifact-host/admin/secrets` (outside the configured `/workflows` prefix) and issues the GET request — confirmable via a Go unit test analogous to the existing `fetcher_test.go` traversal test but targeting `newHTTPFetcher` instead of `newFileFetcher`. [8](#0-7)

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L243-263)
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
```

**File:** core/services/workflows/artifacts/v2/store.go (L131-178)
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
```

**File:** docs/CONFIG.md (L2750-2761)
```markdown
## CRE.WorkflowFetcher
```toml
[CRE.WorkflowFetcher]
URL = '' # Default
```


### URL
```toml
URL = '' # Default
```
URL is override URL for the workflow fetcher service.
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
